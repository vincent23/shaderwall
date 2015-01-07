#ifdef GL_ES
precision mediump float;
#endif
// don't need to touch this
uniform float time;
uniform vec2 resolution;

// the pie is a lie
float PI = acos(-1.);

// write your awesome shadercode here
void main() {
	// this handsome line calculates the current pixel position
	// position is in the [0, 1] range now
	vec2 position = gl_FragCoord.xy / resolution;

	// calculate some edge for the smoothstep() function
	float edge = sin(position.y * 89.);
	edge *= sin(position.y * PI);
	edge *= sin(time);
	// combine all the awesome sines
	edge = .5 + .1 * edge;

	// a little epsilon for smoothing out the smoothstep()
	float epsilon = .02;
	// value contains the black/white value for the pixel
	float value = smoothstep(edge - epsilon, edge + epsilon, position.x);

	// use value for setting the rgb color channels in the [0, 1] range
	// all channels get the same value
	vec3 color = vec3(value);

	// set the calculated color to the pixel
	gl_FragColor = vec4(color, 1.);
}
