const canvas = document.getElementById("render");
const ctx = canvas.getContext("2d");
ctx.font = "16px Arial";
ctx.textAlign = "center";
canvas.width = $(document).height();
canvas.height = $(document).height();
document.body.style.overflow = "hidden";
ctx.imageSmoothingEnabled = true;
var scale = canvas.width / 600;
