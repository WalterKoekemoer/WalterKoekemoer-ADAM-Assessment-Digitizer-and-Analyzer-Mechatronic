let video = document.getElementById("videoElement"); // video is the id of video tag

var localStream;


let display = navigator.mediaDevices.getUserMedia({   video: { facingMode: "environment"},
                                        width: { ideal: 1440 },
                                        height: { ideal: 1024 }
                                    })
    .then(function(stream) {
        video.srcObject = stream;
        video.play();
        localStream = stream;
        
    })
    .catch(function(err) {
        console.log("An error occurred! " + err);
    });