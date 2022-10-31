function onOpenCvReady() {
console.log("OpenCV Init")
    
let video = document.getElementById('videoElement');
let src = new cv.Mat(video.height, video.width, cv.CV_8UC4);
let dst = new cv.Mat(video.height, video.width, cv.CV_8UC1);
let cap = new cv.VideoCapture(video);
$("#UI").modal();

const FPS = 2;
function processVideo() {
    try {
        if (!streaming) {
            src.delete();
            dst.delete();
            return;
        }
        let begin = Date.now();
        
        cap.read(src);
        cv.cvtColor(src, dst, cv.COLOR_RGBA2GRAY);
        // cv.imshow('canvasOutput', dst);  active on ->  <canvas id="canvasOutput" width="320" height="240"></canvas>

        let delay = 1000/FPS - (Date.now() - begin);
        setTimeout(processVideo, delay);
    } catch (err) {
        console.log(err)
    }
};

// schedule the first one.
setTimeout(processVideo, 0);
}