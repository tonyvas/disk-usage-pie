const CANVAS_SIZE_PX = 1000;
const PIE_RADIUS_PX = CANVAS_SIZE_PX / 2 * 0.95;

const PIE_OUTLINE_COLOR = 'black'
const PIE_OUTLINE_WIDTH_PX = 5;

// Run main function when page loads
document.body.onload = () => {
    main();
}

function getContext(){
    // Get the canvas for drawing graph
    let canvas = document.getElementsByTagName('canvas')[0]

    // Setup canvas
    canvas.width = CANVAS_SIZE_PX;
    canvas.height = CANVAS_SIZE_PX;

    // Context for drawing on canvas
    return canvas.getContext('2d');
}

function clearCanvas(context){
    // Clear canvas
    context.clearRect(0, 0, CANVAS_SIZE_PX, CANVAS_SIZE_PX);
}

function drawPieOutline(context){
    // Set line width and color
    context.lineWidth = PIE_OUTLINE_WIDTH_PX;
    context.strokeStyle = PIE_OUTLINE_COLOR;

    // Draw circle
    context.beginPath();
    context.arc(CANVAS_SIZE_PX / 2, CANVAS_SIZE_PX / 2, PIE_RADIUS_PX, 0, 2 * Math.PI);
    context.stroke();
}

function drawGraph(context, tree){
    // Setup graph
    clearCanvas(context)
    drawPieOutline(context)    
}

function main(){
    // Get canvas context
    let context = getContext();

    // Parse JSON
    let tree = JSON.parse(atob(TREE_JSON_BASE64));

    drawGraph(context, tree);
    console.log(JSON.stringify(tree));
}