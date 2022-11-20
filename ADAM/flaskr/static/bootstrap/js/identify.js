var Module = {
    onRuntimeInitialized: function(){
        console.log("opencv init");
        main();
    }
};


function main(){
    let src = new Module.Mat(video.height, video.width, Module.CV_8UC4);
    let dst = new Module.Mat(video.height, video.width, Module.CV_8UC1);
    let my_scan = new Module.Mat(video.height, video.width, Module.CV_8UC4);
    let my_mover  = new Module.Mat(video.height, video.width, Module.CV_8UC1); 
    let cap = new Module.VideoCapture(video);

    var stdnt_x = Math.round(my_scan.cols*$('#pos_x').val());
    var stdnt_y = Math.round(my_scan.rows*$('#pos_y').val());
    var stdnt_width = Math.round(my_scan.cols*$('#my_width').val());
    if (video.width-stdnt_x<stdnt_width)
        stdnt_width = video.width-stdnt_x;
    var stdnt_height = Math.round(my_scan.rows*$('#my_height').val());
    if (video.height-stdnt_y<stdnt_height)
        stdnt_height = video.height-stdnt_y;

    // let students_rect = new Module.Rect(stdnt_x,stdnt_y,stdnt_width,stdnt_height);
    // let scanned = Date.now();
    // let uploaded = Date.now();
    
    var c = document.getElementById("scanner");
    var ctx = c.getContext('2d', { willReadFrequently: true });
    
    class SortableContour {
        perimiterSize;
        areaSize;
        contour;
        
        constructor(fields) {
          Object.assign(this, fields);
        }
    }

    setTimeout(processVideo, 0);
    
    const FPS = 2;
    function processVideo() {
        
        let begin = Date.now();
        let delay = 0;
        if ( $("#hold").prop('checked') == false){
            cap.read(src);
            Module.cvtColor(src, dst, Module.COLOR_RGBA2GRAY);
            my_mover = mover(dst,3,0.6,1,-22); 
            Module.threshold(my_mover, my_mover, 240, 255, Module.THRESH_BINARY);
            // Module.imshow('scanner', my_mover); 
            scan(); 
        }

        delay = 1000/FPS - (Date.now() - begin);
        
        // console.log(delay);
        setTimeout(processVideo, delay);  
    };

    function mover(dst_now,p,alpha,betta,gamma){
        let rect = new Module.Rect(Math.floor(p/2),Math.floor(p/2),dst_now.cols-p,dst_now.rows-p);
        let clear = new Module.Mat.zeros(dst_now.rows-p, dst_now.cols-p, Module.CV_8UC1);
        let src_mover = new Module.Mat.zeros(video.height, video.width, Module.CV_8UC1);
        let dst_mover = new Module.Mat.zeros(video.height, video.width, Module.CV_8UC1);

        let near1 = new Module.Mat();
        let far1 = new Module.Mat();
        let near2 = new Module.Mat();
        let far2 = new Module.Mat();
        let near3 = new Module.Mat();
        let far3 = new Module.Mat();
        let near4 = new Module.Mat();
        let far4 = new Module.Mat();

        let near_rect1 = new Module.Rect(0,0,dst_now.cols-p,dst_now.rows-p);
        let far_rect1 = new Module.Rect(p-1,p-1,dst_now.cols-p,dst_now.rows-p);
        let near_rect2 = new Module.Rect(Math.floor(p/2),0,dst_now.cols-p,dst_now.rows-p);
        let far_rect2 = new Module.Rect(Math.floor(p/2),p-1,dst_now.cols-p,dst_now.rows-p);
        let near_rect3 = new Module.Rect(p-1,0,dst_now.cols-p,dst_now.rows-p);
        let far_rect3 = new Module.Rect(0,p-1,dst_now.cols-p,dst_now.rows-p);
        let near_rect4 = new Module.Rect(Math.floor(p/2),0,dst_now.cols-p,dst_now.rows-p);
        let far_rect4 = new Module.Rect(0,Math.floor(p/2),dst_now.cols-p,dst_now.rows-p);

        near1 = dst_now.roi(near_rect1);
        far1 = dst_now.roi(far_rect1);
        near2 = dst_now.roi(near_rect2);
        far2 = dst_now.roi(far_rect2);
        near3 = dst_now.roi(near_rect3);
        far3 = dst_now.roi(far_rect3);
        near4 = dst_now.roi(near_rect4);
        far4 = dst_now.roi(far_rect4);
        
        Module.addWeighted(near1, 1, far1, 1, gamma, src_mover.roi(rect));
        Module.addWeighted(src_mover.roi(rect), alpha, clear, betta, gamma, dst_mover.roi(rect));
        Module.addWeighted(near2, 1, far2, 1, gamma, src_mover.roi(rect));
        Module.addWeighted(src_mover.roi(rect), alpha, dst_mover.roi(rect), betta, gamma, dst_mover.roi(rect));
        Module.addWeighted(near3, 1, far3, 1, gamma, src_mover.roi(rect));
        Module.addWeighted(src_mover.roi(rect), alpha, dst_mover.roi(rect), betta, gamma, dst_mover.roi(rect));
        Module.addWeighted(near4, 1, far4, 1, gamma, src_mover.roi(rect));
        Module.addWeighted(src_mover.roi(rect), alpha, dst_mover.roi(rect), betta, gamma, dst_mover.roi(rect));

        return dst_mover;
    };

    function scan(){       
        var contours = new Module.MatVector();
        var hierarchy = new Module.Mat();
        Module.Canny(my_mover, my_mover, 100, 255);   
        Module.findContours(my_mover, contours, hierarchy, Module.RETR_TREE, Module.CHAIN_APPROX_SIMPLE);   

        let sortableContours = [];
        if(contours.size() != 0){
            for (let i = 0; i < contours.size(); i++) {
                let cnt = contours.get(i);
                let area = Module.contourArea(cnt, false);
                let perim = Module.arcLength(cnt, false);
    
                sortableContours.push(new SortableContour({ areaSize: area, perimiterSize: perim, contour: cnt }));
            }
        }else{
            Module.imshow('scanner', src);
            return;
        }
        
        
        //Sort 'em
        sortableContours = sortableContours.sort((item1, item2) => { return (item1.areaSize > item2.areaSize) ? -1 : (item1.areaSize < item2.areaSize) ? 1 : 0; }).slice(0, 5);
    
        //Ensure the top area contour has 4 corners (NOTE: This is not a perfect science and likely needs more attention)
        let approx = new Module.Mat();
        Module.approxPolyDP(sortableContours[0].contour, approx, .01 * sortableContours[0].perimiterSize, true);
    
        if (approx.rows == 4) {
           foundContour = approx;
        }
        else{
            Module.imshow('scanner', src);
            scanned = Date.now();
            return;
        }

    
        //Find the corners
        //foundCountour has 2 channels (seemingly x/y), has a depth of 4, and a type of 12.  Seems to show it's a CV_32S "type", so the valid data is in data32S??
        let corner1 = new Module.Point(foundContour.data32S[0], foundContour.data32S[1]);
        let corner2 = new Module.Point(foundContour.data32S[2], foundContour.data32S[3]);
        let corner3 = new Module.Point(foundContour.data32S[4], foundContour.data32S[5]);
        let corner4 = new Module.Point(foundContour.data32S[6], foundContour.data32S[7]);
    
        //Order the corners
        let cornerArray = [{ corner: corner1 }, { corner: corner2 }, { corner: corner3 }, { corner: corner4 }];
        //Sort by Y position (to get top-down)
        cornerArray.sort((item1, item2) => { return (item1.corner.y < item2.corner.y) ? -1 : (item1.corner.y > item2.corner.y) ? 1 : 0; }).slice(0, 5);
    
        //Determine left/right based on x position of top and bottom 2
        let tl = cornerArray[0].corner.x < cornerArray[1].corner.x ? cornerArray[0] : cornerArray[1];
        let tr = cornerArray[0].corner.x > cornerArray[1].corner.x ? cornerArray[0] : cornerArray[1];
        let bl = cornerArray[2].corner.x < cornerArray[3].corner.x ? cornerArray[2] : cornerArray[3];
        let br = cornerArray[2].corner.x > cornerArray[3].corner.x ? cornerArray[2] : cornerArray[3];
    
        //Calculate the max width/height
        let widthBottom = Math.hypot(br.corner.x - bl.corner.x, br.corner.y - bl.corner.y);
        let widthTop = Math.hypot(tr.corner.x - tl.corner.x, tr.corner.y - tl.corner.y);
        let theWidth = (widthBottom > widthTop) ? widthBottom : widthTop;
        let heightRight = Math.hypot(tr.corner.x - br.corner.x, tr.corner.y - br.corner.y);
        let heightLeft = Math.hypot(tl.corner.x - bl.corner.x, tr.corner.y - bl.corner.y);
        let theHeight = (heightRight > heightLeft) ? heightRight : heightLeft;
    
        let finalDestCoords = Module.matFromArray(4, 1, Module.CV_32FC2, [0, 0, theWidth - 1, 0, theWidth - 1, theHeight - 1, 0, theHeight - 1]); //
        let srcCoords = Module.matFromArray(4, 1, Module.CV_32FC2, [tl.corner.x, tl.corner.y, tr.corner.x, tr.corner.y, br.corner.x, br.corner.y, bl.corner.x, bl.corner.y]);
        let dsize = new Module.Size(theWidth, theHeight);
        let M = Module.getPerspectiveTransform(srcCoords, finalDestCoords)
        Module.warpPerspective(src, my_scan, M, dsize, Module.INTER_LINEAR, Module.BORDER_CONSTANT, new Module.Scalar());

        Module.imshow('scanner', my_scan);
        let students = new Module.Mat();
        students = my_scan.roi(new Module.Rect(stdnt_x,stdnt_y,stdnt_width,stdnt_height));
        Module.imshow('students', students);

        if(Date.now()-scanned > 1700 && Date.now()-uploaded > 7000){
            var fd = new FormData();

            var arrayBufferView = new Uint8Array( my_scan.frame );
            var blob = new Blob( [ arrayBufferView ], { type: "image/jpeg" } );
            const scanner = new File([blob], "scanner.png", {
                type: 'image/png'
            });
            arrayBufferView = new Uint8Array( students.frame );
            blob = new Blob( [ arrayBufferView ], { type: "image/jpeg" } );
            const students = new File([blob], "students.png", {
                type: 'image/png'
            });
            
            fd.append("image", scanner);
            fd.append("image", students);

            uploaded = Date.now();
            $("#scan").submit();

            $(document).on('submit','#scan',function(e) {
            e.preventDefault();
            $.ajax({
                type:'POST',
                url:"{{url_for('adam.scan')}}",
                data:fd,
                dataType: "json",
                success: function(response_data){
                    console.log(response_data);
                },
                error : function(request,error)
                {
                    console.log([request,error]);
                }
            })
            });
        }
    }

    $( "#my_width" ).on( "input", function() {
        
        stdnt_width = Math.round(my_scan.cols*$('#my_width').val());
        if (my_scan.cols-stdnt_x<stdnt_width && my_scan.cols>stdnt_x)
            stdnt_width = my_scan.cols-stdnt_x;

        let students = new Module.Mat();
        students = my_scan.roi(new Module.Rect(stdnt_x,stdnt_y,stdnt_width,stdnt_height));
        Module.imshow('students', students);

        Module.imshow('scanner', my_scan);
        ctx.beginPath();
        ctx.lineWidth = "5";
        ctx.strokeStyle = "#6C3D91";
        ctx.rect(stdnt_x,stdnt_y,stdnt_width,stdnt_height);
        ctx.stroke();

    });

    $( "#my_height" ).on( "input", function() {

        stdnt_height = Math.round(my_scan.rows*$('#my_height').val());
        if (my_scan.rows-stdnt_y<stdnt_height && my_scan.rows>stdnt_y)
            stdnt_height = my_scan.rows-stdnt_y;

        let students = new Module.Mat();
        students = my_scan.roi(new Module.Rect(stdnt_x,stdnt_y,stdnt_width,stdnt_height));
        Module.imshow('students', students);

        Module.imshow('scanner', my_scan);
        ctx.beginPath();
        ctx.lineWidth = "5";
        ctx.strokeStyle = "#6C3D91";
        ctx.rect(stdnt_x,stdnt_y,stdnt_width,stdnt_height);
        ctx.stroke();
    
    });
    
    $( "#pos_x" ).on( "input", function() {
        
        let x = Math.round(my_scan.cols*$('#pos_x').val());
        if (x + stdnt_width < my_scan.cols)
            stdnt_x = x;

        let students = new Module.Mat();
        students = my_scan.roi(new Module.Rect(stdnt_x,stdnt_y,stdnt_width,stdnt_height));
        Module.imshow('students', students);
        
        Module.imshow('scanner', my_scan);
        ctx.beginPath();
        ctx.lineWidth = "5";
        ctx.strokeStyle = "#6C3D91";
        ctx.rect(stdnt_x,stdnt_y,stdnt_width,stdnt_height);
        ctx.stroke();
    
    });


    $( "#pos_y" ).on( "input", function() {

        let y = Math.round(my_scan.rows*$('#pos_y').val());
        if (y + stdnt_height < my_scan.rows)
            stdnt_y = y;

        let students = new Module.Mat();
        students = my_scan.roi(new Module.Rect(stdnt_x,stdnt_y,stdnt_width,stdnt_height));
        Module.imshow('students', students);

        Module.imshow('scanner', my_scan);
        ctx.beginPath();
        ctx.lineWidth = "5";
        ctx.strokeStyle = "#6C3D91";
        ctx.rect(stdnt_x,stdnt_y,stdnt_width,stdnt_height);
        ctx.stroke();
    
    });
    
    $("#hold").on("change",function(){
        if ( $(this).prop('checked') ){
            $("#upload").hide();
            $('#pos_x').prop('disabled',false);
            $('#pos_y').prop('disabled',false);
            $('#my_height').prop('disabled',false);
            $('#my_width').prop('disabled',false);
            
            Module.imshow('scanner', my_scan);
            let students = new Module.Mat();
            students = my_scan.roi(new Module.Rect(stdnt_x,stdnt_y,stdnt_width,stdnt_height));
            Module.imshow('students', students);

            ctx.beginPath();
            ctx.lineWidth = "5";
            ctx.strokeStyle = "#6C3D91";
            ctx.rect(stdnt_x,stdnt_y,stdnt_width,stdnt_height);
            ctx.closePath();
            ctx.stroke();
        }else{
            $("#upload").show();
            $('#pos_x').prop('disabled',true);
            $('#pos_y').prop('disabled',true);
            $('#my_height').prop('disabled',true);
            $('#my_width').prop('disabled',true);
        }
    });
}

$("#ADAM").on('show.bs.modal', function(){
    
});

$("#ADAM").on('hide.bs.modal', function(){
    // if(localStream){
    //     localStream.getTracks().forEach(function(track) {
    //         track.stop();
    //     });
    // }
});

$("#ADAM").on('hidden.bs.modal', function () {
    // $("#ADAM").modal();
    // if(localStream){
    //     navigator.mediaDevices.getUserMedia({   video: { facingMode: "environment"},
    //                                 width: { exact: 1440 },
    //                                 height: { exact: 1024 }
    //                             })
    //     .then(function(stream) {
    //         video.srcObject = stream;
    //         video.play();
    //         localStream = stream;
            
    //     })
    //     .catch(function(err) {
    //         console.log("An error occurred! " + err);
    //     });
    // }
});