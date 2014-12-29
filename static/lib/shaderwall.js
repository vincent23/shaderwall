var Shaderwall = function() {
	this.errors = [];
	this.time = 0;
	this.quality = 1;

	CodeMirror.registerHelper("lint", "glsl", function(text) {
		return this.errors;
	}.bind(this));

	this.editor = CodeMirror(document.body, {
		value: shaderSource,
		mode: "glsl",
		lineNumbers: true,
		indentWithTabs: true,
		indentUnit: 4,
		lineWrapping: true,
		gutters: ["CodeMirror-lint-markers"],
		lint: true,
		scrollbarStyle: "null",
		theme: "zenburn",
		extraKeys: {"Ctrl-Space": "autocomplete"},
	});

	this.canvas = document.getElementById("glcanvas");
	if(wall_mode) {
		$('.CodeMirror')[0].style.display = 'none';
		this.canvas.style.top = "0px";
		this.canvas.style.height = "100%";
	}
	this.gl = this.initGL(this.canvas);

	this.glState = {
		posAttribute: -1,
		resolutionUniform: -1,
		timeUniform: -1,
	};

	this.updateSize();
	this.workingSource = "";
	this.reloadShaders(this.editor.getValue());
	var compileTimer = null;
	this.editor.on("change", (function(editor, changes, source) {
		if (source === this) {
			return;
		}
		clearTimeout(compileTimer);
		compileTimer = setTimeout((function() {
			this.reloadShaders(this.editor.getValue());
			CodeMirror.signal(this.editor, 'change', this.editor, {}, this);
		}).bind(this), 200);
	}).bind(this));

	this.resume();
};

Shaderwall.prototype.initGL = function(canvas) {
	var gl = null;
	try {
		gl = canvas.getContext("webgl", {preserveDrawingBuffer: true});
	} catch(e) {
		try {
			gl = canvas.getContext("experimental-webgl", {preserveDrawingBuffer: true});
		} catch(e) {
		}
	}

	if(!gl) {
		// TODO display error
		alert("Kein GL!");
	} else {
		var rectBuffer = gl.createBuffer();
		gl.bindBuffer(gl.ARRAY_BUFFER, rectBuffer);

		var vertices = [
			1.0, 1.0,
			-1.0, 1.0,
			1.0, -1.0,
			-1.0, -1.0,
		];
		gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(vertices), gl.STATIC_DRAW);
	}
	return gl;
};

Shaderwall.prototype.compileShader = function(source, type) {
	var gl = this.gl;
	var shader = gl.createShader(type);
	gl.shaderSource(shader, source);
	gl.compileShader(shader);
	if(!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
		// der (noch nicht ganz so) gute!
		var errorRegex = /ERROR:.*:([0-9]+): (.*)/;
		gl.getShaderInfoLog(shader).split('\n').forEach(function(line) {
			var match = line.match(errorRegex);
			if (match !== null) {
				var line = match[1] - 1;
				var error_message = match[2];
				this.errors.push({from: CodeMirror.Pos(line, 0), to: CodeMirror.Pos(line), message: error_message});
			}
		}.bind(this));
		console.log(gl.getShaderInfoLog(shader));
		return null;
	} else {
		return shader;
	}
};

Shaderwall.prototype.reloadShaders = function(fragmentSource) {
	this.errors = [];
	var gl = this.gl;
	var vertexSource = "#ifdef GL_ES\nprecision mediump float;\n#endif\nattribute vec2 pos;\nvoid main(void) {\ngl_Position = vec4(pos, 0.0, 1.0);\n}\n";
	var fragment = this.compileShader(fragmentSource, gl.FRAGMENT_SHADER);
	if (fragment === null) {
		return;
	}
	var vertex = this.compileShader(vertexSource, gl.VERTEX_SHADER);

	var program = gl.createProgram();
	gl.attachShader(program, fragment);
	gl.attachShader(program, vertex);
	gl.linkProgram(program);
	if(!gl.getProgramParameter(program, gl.LINK_STATUS)) {
		//alert("linking failed");
		return;
	}

	this.workingSource = fragmentSource;
	gl.useProgram(program);
	var posAttribute = gl.getAttribLocation(program, "pos");
	gl.enableVertexAttribArray(posAttribute);
	this.glState.posAttribute = posAttribute;
	this.glState.resolutionUniform = gl.getUniformLocation(program, "resolution");
	this.glState.timeUniform = gl.getUniformLocation(program, "time");
};

Shaderwall.prototype.draw = function(time) {
	this.time = time;
	var gl = this.gl;
	var canvas = this.canvas;
	gl.vertexAttribPointer(this.glState.posAttribute, 2, gl.FLOAT, false, 0, 0);
	gl.uniform2f(this.glState.resolutionUniform, canvas.width, canvas.height);
	gl.uniform1f(this.glState.timeUniform, time / 1000);
	gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);

	if (this.running)
		window.requestAnimationFrame(this.draw.bind(this));
};

Shaderwall.prototype.resume = function() {
	this.running = true;
	this.draw(this.time);
}

Shaderwall.prototype.pause = function() {
	this.running = false;
}

Shaderwall.prototype.updateSize = function() {
	var canvas = this.canvas;
	var newWidth = document.documentElement.clientWidth;
	var newHeight = document.documentElement.clientHeight - (wall_mode ? 0 : 50 /*height of navbar*/);
	canvas.width = newWidth / this.quality;
	canvas.height = newHeight / this.quality;
	this.gl.viewport(0, 0, canvas.width, canvas.height);
	canvas.style.width = newWidth + 'px';
	canvas.style.height = newHeight + 'px';
};

Shaderwall.prototype.screenshot = function() {
	var screenshot_scale = 2;

	var gl = this.gl;
	var canvas = this.canvas;
	var oldheight = canvas.height;
	var oldwidth = canvas.width;
	canvas.height = screenshot_height * screenshot_scale;
	canvas.width = screenshot_width * screenshot_scale;
	gl.vertexAttribPointer(this.glState.posAttribute, 2, gl.FLOAT, false, 0, 0);
	gl.uniform2f(this.glState.resolutionUniform, screenshot_width * screenshot_scale, screenshot_height * screenshot_scale);
	gl.uniform1f(this.glState.timeUniform, this.time / 1000);
	gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);

	var dummycanvas = document.createElement("canvas");
	dummycanvas.height = screenshot_height;
	dummycanvas.width = screenshot_width;
	var dummycontext = dummycanvas.getContext("2d");
	dummycontext.drawImage(canvas, 0, 0, dummycanvas.width, dummycanvas.height)

	var screenshot = dummycanvas.toDataURL("image/png");
	canvas.height = oldheight;
	canvas.width = oldwidth;
	return screenshot
}

$(document).ready(function() {
	var shaderwall = new Shaderwall();
	$('#pause-button').click(function(e) {
		if (shaderwall.running) {
			shaderwall.pause();
			$(e.target).html("Resume");
			$(e.target).addClass("active");
		} else {
			shaderwall.resume();
			$(e.target).html("Pause");
			$(e.target).removeClass("active");
		}
	});
	$('#save-button').click(function () {
		var source = shaderwall.workingSource;
		var screenshot = shaderwall.screenshot();

		$.post(save_url, { 'source': source, 'screenshot': screenshot, 'authcode': authcode, },function(data) {
			console.log(data);
			if(data['redirect']) {
				self.location.href = '/edit/' + data['id'] + '?authcode=' + data['authcode'];
			}else if(data['id'] > 0){
				document.getElementById('save-button').innerHTML = 'Saved!';
				$('#save-button').removeClass("btn-default");
				$('#save-button').addClass("btn-success");
				setTimeout(function() {
					$('#save-button').addClass("btn-default");
					$('#save-button').removeClass("btn-success");
					document.getElementById('save-button').innerHTML = save_button_text;
				}, 2000);
			}else{
				alert("An error occured. Please try again later.");
			}
		}, "json").fail(function() { alert( "An error occured. Please try again later." ); });
	});

	$('#vote-up-button').click(function(){
		$.post(
			'/vote',
			{'id': shaderId, 'vote': 'up'},
			function(){
				$('#vote-up-button').addClass('disabled');
				$('#vote-up-button').addClass('btn-success');
				$('#vote-piggy-button').addClass('disabled');
				$('#vote-down-button').addClass('disabled');
			},
			'json'
		).fail(function(jqxhr){
			if(jqxhr.status == 403){
				$('#vote-up-button').addClass('disabled');
				$('#vote-piggy-button').addClass('disabled');
				$('#vote-down-button').addClass('disabled');
				alert("You may not vote twice. Your first vote is final.");
			} else {
				alert("An error occured: " + jqxhr.status);
			}
		});
	});
	$('#vote-piggy-button').click(function(){
		$('#vote-up-button').addClass('disabled');
		$('#vote-piggy-button').addClass('disabled');
		$('#vote-piggy-button').addClass('btn-primary');
		$('#vote-down-button').addClass('disabled');
	});
	$('#vote-down-button').click(function(){
		$.post(
			'/vote',
			{'id': shaderId, 'vote': 'down'},
			function(){
				$('#vote-up-button').addClass('disabled');
				$('#vote-piggy-button').addClass('disabled');
				$('#vote-down-button').addClass('disabled');
				$('#vote-down-button').addClass('btn-danger');
			},
			'json'
		).fail(function(jqxhr){
			if(jqxhr.status == 403){
				$('#vote-up-button').addClass('disabled');
				$('#vote-piggy-button').addClass('disabled');
				$('#vote-down-button').addClass('disabled');
				alert("You may not vote twice. Your first vote is final.");
			} else {
				alert("An error occured: " + jqxhr.status);
			}
		});
	});

	var hidden = false;
	var codeMirrorDisplay = $('.CodeMirror')[0].style.display;
	$('#hide-button').click(function(e) {
		hidden = !hidden;
		if (hidden) {
			$(e.target).html("Show code");
			$(e.target).addClass("active");
			$('.CodeMirror')[0].style.display = 'none';
		} else {
			$(e.target).html("Hide code");
			$(e.target).removeClass("active");
			$('.CodeMirror')[0].style.display = codeMirrorDisplay;
		}
	});

	$('#mode-selector').change(function(e) {
		var val = $(e.target).val();
		var editor = shaderwall.editor;
		if (val === 'notepad') {
			editor.setOption('keyMap', 'default');
			editor.setOption('vimMode', false);
		} else if (val === 'vim') {
			editor.setOption('vimMode', true);
		} else if (val === 'emacs') {
			editor.setOption('keyMap', 'emacs');
			editor.setOption('vimMode', false);
		} else if (val === 'sublime') {
			editor.setOption('keyMap', 'sublime');
			editor.setOption('vimMode', false);
		}
	});

	$('#quality-selector').change(function(e) {
		shaderwall.quality = $(e.target).val();
		shaderwall.updateSize();
	});

	// register a callback function for window resizes
	// but only call the actual resize function if enough time has elasped since the last time
	// code from mozilla website
	// this callback could be fired rapidly
	window.addEventListener("resize", resizeThrottler, false);
	var resizeTimeout;
	function resizeThrottler() {
		// ignore resize events as long as an actualResizeHandler execution is in the queue
		if ( !resizeTimeout ) {
			// some kind of queue
			resizeTimeout = setTimeout(function() {
				resizeTimeout = null;
				actualResizeHandler();

			// The actualResizeHandler will execute at a rate of 5fps
			}, 100);
		}
	}
	function actualResizeHandler() {
		shaderwall.updateSize();
	}
});

