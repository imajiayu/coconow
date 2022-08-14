
<template>
        <div class="resize" id = "resize" ref="resize">
            
        </div>

</template>

<style scoped>
/*====================================================
�϶���
====================================================*/

 
.resize{
  display: inline-block;
  vertical-align: top;
  width:5px;
  height:100%;
  background-color:rgb(228, 228, 228);
  cursor: w-resize;
  /*float:left;*/
}
 
.right{
  display: inline-block;
  vertical-align: top;
  /*float:left;*/
  width: 29%;
  height:100%;
  background-color: white;
}
</style>



<script setup>
import { onMounted, ref } from "vue";
const props = defineProps({
    lid:{
        type:String,
        required:true,
    },
    rid:{
        type:String,
        required:true,
    },
    rbox:{
        type:String,
        required:true,
    },
    leftstart:{
        type:Number,
        required:true,
        default:0
    }
})

onMounted(() => {
    //==============================================================
    // �϶���
    //==============================================================
    
    var resize = document.getElementById('resize');
    var lleft = document.getElementById(props.lid);
    var box = document.getElementById(props.rbox);
    
    var rright = document.getElementById(props.rid);
    // console.log("rright",rright);
    var rw = resize.offsetWidth;
    var w = box.offsetWidth;
    resize.onmousedown = function (e) {
        var startX = e.clientX;
        resize.left = resize.offsetLeft;

        // ����϶��¼�?
        document.onmousemove = function (e) {
        //console.log("resize.left", resize, e.clientX - startX);
        var llleft = props.leftstart;
        var moveLen = resize.left + (e.clientX - startX) -llleft;  // lleft �������Ŀ���
        // console.log('moveLen', moveLen);
        // console.log('w-rw-moveLen', w-rw-moveLen);
        if ((w-rw-moveLen > 10) && (moveLen > 100)) {
            if (w-rw-moveLen>20 && rright.style.display != "inline-block")
                rright.style.display = "inline-block";
            //console.log("moveLen", moveLen);
            //console.log("lleft.style.width", lleft.style.width);
            resize.style.left = moveLen;
            lleft.style.width = moveLen + 'px';
            rright.style.width = (w - rw - moveLen) + 'px';
        }
        if ((w-rw-moveLen <= 30)) {
            // console.log("hide right");
            rright.style.display = "none";
        }
        }
        // ����ɿ��¼�?
        document.onmouseup = function () {
        document.onmousemove = null;
        document.onmouseup = null;
        resize.releaseCapture && resize.releaseCapture();
        }
        resize.setCapture && resize.setCapture();
    }  
})
</script>
