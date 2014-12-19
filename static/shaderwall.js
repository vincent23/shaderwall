var Shaderwall = function() {
	this.editor = CodeMirror(document.body, {
		value: "#ifdef GL_ES\nprecision mediump float;\n#endif\nvoid main(void)\n{\n\tgl_FragColor = vec4(1.0, 0.0, 0.0, 1.0);\n}\n",
		mode: "clike",
		lineNumbers: true,
		indentWithTabs: true,
		indentUnit: 4,
		lineWrapping: true,
	});

	this.canvas = document.getElementById("glcanvas");
	this.gl = this.initGL(this.canvas);

	this.glState = {
		posAttribute: -1,
		resolutionUniform: -1,
		timeUniform: -1,
	};

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
		gl = canvas.getContext("webgl");
	} catch(e) {
		try {
			gl = canvas.getContext("experimental-webgl");
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
		//alert("Shader compile error: " + gl.getShaderInfoLog(shader));
		console.log(gl.getShaderInfoLog(shader));
		return null;
	} else {
		return shader;
	}
};

Shaderwall.prototype.reloadShaders = function(fragmentSource) {
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

$(document).ready(function() {
	var shaderwall = new Shaderwall();
});
