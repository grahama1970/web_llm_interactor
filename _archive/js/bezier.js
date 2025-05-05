/**
 * Bezier curve mouse movement generator
 * Creates realistic human-like mouse movements
 */

/**
 * Generates a realistic mouse movement path using cubic Bézier curves
 * 
 * @param {number} startX - Starting X coordinate
 * @param {number} startY - Starting Y coordinate  
 * @param {number} endX - Ending X coordinate
 * @param {number} endY - Ending Y coordinate
 * @param {number} steps - Number of points to generate along the path
 * @param {number} randomizationFactor - Factor for randomizing control points (0-1)
 * @returns {Array} Array of {x, y} coordinate points
 */
function generateBezierPath(startX, startY, endX, endY, steps = 10, randomizationFactor = 0.2) {
  // Ensure steps is a positive integer with a minimum value
  steps = Math.max(5, Math.floor(steps));
  
  // Calculate distance between start and end points
  const distance = Math.sqrt(Math.pow(endX - startX, 2) + Math.pow(endY - startY, 2));
  
  // Scale randomization based on distance and randomization factor
  const randomFactor = Math.min(100, distance * randomizationFactor);
  
  // Generate control points with appropriate randomization
  const cp1x = startX + (endX - startX) * 0.3 + (Math.random() * randomFactor - randomFactor/2);
  const cp1y = startY + (endY - startY) * 0.3 + (Math.random() * randomFactor - randomFactor/2);
  const cp2x = startX + (endX - startX) * 0.7 + (Math.random() * randomFactor - randomFactor/2);
  const cp2y = startY + (endY - startY) * 0.7 + (Math.random() * randomFactor - randomFactor/2);

  // Generate points along the Bézier curve
  const path = [];
  for (let t = 0; t <= 1; t += 1 / steps) {
    // Cubic Bézier curve formula
    const x = (1 - t) ** 3 * startX +
              3 * (1 - t) ** 2 * t * cp1x +
              3 * (1 - t) * t ** 2 * cp2x +
              t ** 3 * endX;
    const y = (1 - t) ** 3 * startY +
              3 * (1 - t) ** 2 * t * cp1y +
              3 * (1 - t) * t ** 2 * cp2y +
              t ** 3 * endY;
    
    // Add slight jitter to make movement more realistic
    const jitterX = Math.random() * 2 - 1; // -1 to 1 pixels
    const jitterY = Math.random() * 2 - 1; // -1 to 1 pixels
    
    path.push({ 
      x: x + jitterX, 
      y: y + jitterY 
    });
  }
  
  return path;
}

// Additional helper for more complex mouse patterns (optional)
function generateRandomMouseMovements(count, minX, maxX, minY, maxY) {
  const movements = [];
  let lastX = minX + Math.random() * (maxX - minX);
  let lastY = minY + Math.random() * (maxY - minY);
  
  for (let i = 0; i < count; i++) {
    const newX = Math.max(minX, Math.min(maxX, lastX + (Math.random() * 200 - 100)));
    const newY = Math.max(minY, Math.min(maxY, lastY + (Math.random() * 200 - 100)));
    
    const path = generateBezierPath(lastX, lastY, newX, newY, 10);
    movements.push(...path);
    
    lastX = newX;
    lastY = newY;
  }
  
  return movements;
}

module.exports = { 
  generateBezierPath,
  generateRandomMouseMovements
};