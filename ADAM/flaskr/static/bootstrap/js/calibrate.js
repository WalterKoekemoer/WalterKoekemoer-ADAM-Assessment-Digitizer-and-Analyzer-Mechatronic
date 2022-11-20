var Module = {
    onRuntimeInitialized: function() {
        console.log("opencv init");
        $("#ADAM").modal();
    }
};

$("#ADAM").on('show.bs.modal', function(){
    let src = new Module.Mat(video.height, video.width, Module.CV_8UC4),
    dst = new Module.Mat(video.height, video.width, Module.CV_8UC1),
    cap = new Module.VideoCapture(video),
    dsize = new Module.Size(288, 216),
    corners = new Module.Mat(),
    image_points = new Module.MatVector(),
    object_points = new Module.MatVector();

    document.getElementById('calibrate').addEventListener("click",function(){
        // let canvas = document.getElementById('canvasOutput');
        // canvas.style.width = "288px";
        // canvas.style.height = "216px";


        cap.read(src);
        Module.cvtColor(src, dst, Module.COLOR_RGBA2GRAY);
        
        var board_size = new Module.Size(7, 7);

        var found = Module.findChessboardCorners(dst, board_size, corners, 1|4);
    
        if (found) {
            Module.cornerSubPix(dst, corners, new Module.Size(5, 5), new Module.Size(-1, -1), 
            new Module.TermCriteria(3, 30, 0.1));
            Module.drawChessboardCorners(dst, board_size, corners, true);
        }
        
        var obj = new Module.Mat(board_height*board_width, 1, Module.CV_32FC3);
        var view = obj.data32F;
    
        for (var i = 0; i < board_height; i++)
        for (var j = 0; j < board_width; j++) {
    
            view[3*i*board_width + j*3 + 0] = j * square_size;
            view[3*i*board_width + j*3 + 1] = i * square_size;
            view[3*i*board_width + j*3 + 2] = 0;
        }
    
        if (found) {
        image_points.push_back(corners);
        object_points.push_back(obj);
        }
    
        Module.resize(dst, dst, dsize, 0, 0, Module.INTER_AREA);
        Module.imshow('canvasOutput', dst);
        // return {imgs: image_points,
        //         objs: object_points,
        //         img_size: img_size};
    
        // Module.resize(src, dst, dsize, 0, 0, Module.INTER_AREA);
        // Module.imshow('canvasOutput', dst);
        // src.delete(); dst.delete();
    });
});

$("#ADAM").on('hide.bs.modal', function(){
});

$("#ADAM").on('hidden.bs.modal', function () {
});