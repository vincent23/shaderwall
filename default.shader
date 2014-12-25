#ifdef GL_ES
precision mediump float;
#endif
uniform float time;
uniform vec2 resolution;

// Colors
vec4 BACKGROUND = vec4(0.0, 0.0, 0.0, 1.0);
vec4 CIRCLE = vec4(1.0, 1.0, 1.0, 1.0);
vec4 BLOCK_0 = vec4(0.25, 0.08, 0.36, 1);
vec4 BLOCK_1 = vec4(0.43, 0.31, 0.71, 1);
vec4 BLOCK_2 = vec4(1.0, 0.63, 0.0, 1);
vec4 BLOCK_3 = vec4(1.0, 0.50, 0.20, 1);
vec4 BLOCK_4 = vec4(1.0, 0.35, 0.27, 1);

float SIZE = resolution.y/16.0;

float BLOCK_OFFSET = 1.0*SIZE;
float LOGO_OFFSET = 1.25*SIZE;

float RADIUS = 4.0*SIZE;

bool check_block_boundaries(vec2 diff, int box) {
    return (
        diff.x < SIZE/2.0 &&
        diff.x > -SIZE/2.0 &&
        diff.y+BLOCK_OFFSET <= -SIZE*(0.0+float(box)) &&
        diff.y+BLOCK_OFFSET > -SIZE*(1.0+float(box))
    );
}

void main(void) {
    // The center of the circle
    vec2 center = vec2(resolution.x/2.0,resolution.y/2.0) - vec2(0.0, LOGO_OFFSET);

    // Current pixel location
    vec2 loc = gl_FragCoord.xy;

    // How far we are from the center
    float radius=length(loc-center);

    // Difference between center of circle and current pixel
    vec2 diff = center-loc;

    // Fill background
    gl_FragColor = BACKGROUND;

    // Draw circle (with cut on top)
    if ( radius < RADIUS && radius > RADIUS-SIZE && ( loc.y < center.y || diff.x < -SIZE*1.5 || diff.x > SIZE*1.5 ) ) {
        gl_FragColor = CIRCLE;
    }

    // Create blocks (from bottom to top)
    if ( check_block_boundaries( diff, 0 ) ) {
        gl_FragColor = BLOCK_0;
    } else if ( check_block_boundaries( diff, 1 ) ) {
        gl_FragColor = BLOCK_1;
    } else if ( check_block_boundaries( diff, 2 ) ) {
        gl_FragColor = BLOCK_2;
    } else if ( check_block_boundaries( diff, 3 ) ) {
        gl_FragColor = BLOCK_3;
    } else if ( check_block_boundaries( diff, 4 ) ) {
        gl_FragColor = BLOCK_4;
    }
}



