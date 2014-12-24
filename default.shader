#ifdef GL_ES
precision mediump float;
#endif
uniform float time;
uniform vec2 resolution;

#define BACKGROUND vec4(0.0, 0.0, 0.0, 1.0)
#define CIRCLE vec4(1.0, 1.0, 1.0, 1.0)

#define C1 vec4(0.25, 0.08, 0.36, 1)
#define C2 vec4(0.43, 0.31, 0.71, 1)
#define C3 vec4(1.0, 0.63, 0.0, 1)
#define C4 vec4(1.0, 0.50, 0.20, 1)
#define C5 vec4(1.0, 0.35, 0.27, 1)

#define SIZE resolution.y/16.0

#define X1 6.25*SIZE
#define OFFSET_Y 1.375*SIZE
#define RADIUS 4.0*SIZE

void main(void) {
    // the center of the circle
    vec2 center = vec2(resolution.x/2.0,resolution.y/2.0) - vec2(0.0, OFFSET_Y);

    // current pixel location
    vec2 loc = gl_FragCoord.xy;

    // how far we are from the center
    float radius=length(loc-center);

	vec2 diff = center-loc;
	diff.y += SIZE*7.375;

	// CIRCLE (WITH "CUT")
	if (radius<RADIUS && radius>(RADIUS-SIZE) && (diff.y > RADIUS+SIZE || diff.x < -SIZE*1.5 || diff.x > SIZE*1.5)) {
        gl_FragColor = CIRCLE;
	// BLOCKS FROM BOTTOM TO TOP
	} else if ( diff.x < SIZE/2.0 && diff.x > -SIZE/2.0 && diff.y <= X1-SIZE*0.0 && diff.y > X1-SIZE*1.0) {
        gl_FragColor = C1;
	} else if ( diff.x < SIZE/2.0 && diff.x > -SIZE/2.0 && diff.y <= X1-SIZE*1.0 && diff.y > X1-SIZE*2.0) {
        gl_FragColor = C2;
	} else if ( diff.x < SIZE/2.0 && diff.x > -SIZE/2.0 && diff.y <= X1-SIZE*2.0 && diff.y > X1-SIZE*3.0) {
        gl_FragColor = C3;
	} else if ( diff.x < SIZE/2.0 && diff.x > -SIZE/2.0 && diff.y <= X1-SIZE*3.0 && diff.y > X1-SIZE*4.0) {
        gl_FragColor = C4;
	} else if ( diff.x < SIZE/2.0 && diff.x > -SIZE/2.0 && diff.y <= X1-SIZE*4.0 && diff.y > X1-SIZE*5.0) {
        gl_FragColor = C5;
	// BACKGROUND
	} else {
        gl_FragColor = BACKGROUND;
	}
}
