var Shaderwall = function() {
	this.errors = [];

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
	});

	this.canvas = document.getElementById("glcanvas");
	this.gl = this.initGL(this.canvas);

	this.glState = {
		posAttribute: -1,
		resolutionUniform: -1,
		timeUniform: -1,
	};

	this.updateSize();
	this.reloadShaders(this.editor.getValue());
	this.editor.on("change", (function() {
		this.reloadShaders(this.editor.getValue());
		this.draw();
	}).bind(this));
	this.draw(0.0);
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
	var vertex = this.compileShader(vertexSource, gl.VERTEX_SHADER);

	var program = gl.createProgram();
	gl.attachShader(program, fragment);
	gl.attachShader(program, vertex);
	gl.linkProgram(program);
	if(!gl.getProgramParameter(program, gl.LINK_STATUS)) {
		//alert("linking failed");
	}

	gl.useProgram(program);
	var posAttribute = gl.getAttribLocation(program, "pos");
	gl.enableVertexAttribArray(posAttribute);
	this.glState.posAttribute = posAttribute;
	this.glState.resolutionUniform = gl.getUniformLocation(program, "resolution");
	this.glState.timeUniform = gl.getUniformLocation(program, "time");
};

Shaderwall.prototype.draw = function(time) {
	var gl = this.gl;
	gl.vertexAttribPointer(this.glState.posAttribute, 2, gl.FLOAT, false, 0, 0);
	gl.uniform2f(this.glState.resolutionUniform, 640, 480);
	gl.uniform1f(this.glState.timeUniform, time / 1000);
	gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
	window.requestAnimationFrame(this.draw.bind(this));
};

Shaderwall.prototype.updateSize = function() {
	var canvas = this.canvas;
	var newWidth = document.documentElement.clientWidth;
	var newHeight = document.documentElement.clientHeight - 50 /*height of navbar*/;
	if (canvas.width != newWidth || canvas.height != newHeight) {
		canvas.width = newWidth;
		canvas.height = newHeight;
		this.gl.viewport(0, 0, newWidth, newHeight);
	}
};

$(document).ready(function() {
	var shaderwall = new Shaderwall();
	$('#save-button').click(function () {
		var source = shaderwall.editor.getValue();
		var canvas = document.getElementById("glcanvas");
		var dummycanvas = document.createElement("canvas");
		dummycanvas.height = 300;
		dummycanvas.width = 400;
		var dummycontext = dummycanvas.getContext("2d");
		dummycontext.drawImage(canvas, 0, 0, dummycanvas.width, dummycanvas.height)
		var screenshot = dummycanvas.toDataURL("image/png");

		$.post(save_url, { 'source': source, 'screenshot': screenshot, 'authcode': authcode, },function(data) {
			console.log(data);
			if(data['id'] >= 0) {
				self.location.href = '/edit/' + data['id'] + '?authcode=' + data['authcode'];
			}else{
				alert(data);
			}
		}, "json");
	});

	$('#mode-selector').change(function() {
		var val = $('#mode-selector').val();
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

