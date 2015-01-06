#ifdef GL_ES
precision mediump float;
#endif
// don't need to touch this
uniform float time;
uniform vec2 resolution;
uniform sampler2D tex;

// write your awesome shadercode here

float rand(vec2 co){
    return fract(sin(dot(co.xy ,vec2(12.9898,78.233))) * 43758.5453);
}

void main() {
	vec2 tpos = gl_FragCoord.xy / resolution;
	vec2 stpos = (tpos - 0.5) * 0.98 + 0.5;
	vec3 val = vec3(0);

	for(int i = 0; i < 100; i++) {
		vec2 spos = vec2(rand(vec2(time + float(i), time * 1.1234)), rand(vec2(time + float(i) + 0.123456, time * 0.9))) * resolution;
		float d = length(gl_FragCoord.xy - spos);
		float r = rand(vec2(time + spos)) * 4.0;
		vec3 rgb = vec3(rand(tpos + time), rand(tpos + time + 1.0), rand(tpos + time + 2.0));
		val += (1.0 - smoothstep(0.0, r, d)) * rgb;
	}

	vec4 color = vec4(val, 1.0);
	gl_FragColor = color + texture2D(tex, stpos) - 0.003;
}
