
import { io } from "https://cdn.socket.io/4.3.2/socket.io.esm.min.js";

const socket = io();

socket.on('connect', function(){
console.log("Init")
});

var canvas = document.getElementById('canvas');
var context = canvas.getContext('2d');
const video = document.querySelector("#videoElement");
var hideVideo = document.getElementsByClassName("hideVideo")[0];
hideVideo.style.display = "none";
canvas.style.display = "none";


if (navigator.mediaDevices.getUserMedia) {
    let stream = null;

    try {
        stream = await navigator.mediaDevices.getUserMedia(constraints);
        /* use the stream */
    } catch (err) {
        /* handle the error */
    }
    navigator.mediaDevices.getUserMedia({   video: { frameRate: { ideal: 1, max: 1 } },
                                            width: { ideal: 1440 },
                                            height: { ideal: 1080 }
                                        })
    .then(function (stream) {
        video.srcObject = stream;
        video.play();
    })
    .catch(function (err0r) {

    });
}

const FPS = 1;
setInterval(() => {
context.drawImage(video, 0, 0, 1440, 1080);
var data = canvas.toDataURL('image/jpg',0.95);
socket.emit('image', data);
}, 1000/FPS);


socket.on('response_back', function(image){
photo.setAttribute('src', image );
});