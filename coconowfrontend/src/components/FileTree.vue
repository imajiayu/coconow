
<template>
<el-container style="height:100%">
      
  <div id="treemenu" v-show="TreeMenuVisible" class="menu">
  <div class="contextmenu_item" @click="newDirForm.visible=true">新建目录</div>
  <div class="contextmenu_item" @click="newFileForm.visible=true">新建文件</div>
  <div class="contextmenu_item" @click="deleteDir">删除目录</div>
  <div class="contextmenu_item" @click="uploadForm.visible=true">上传文件</div>
  </div>
  <div id="filemenu" v-show="FileMenuVisible" class="menu">
  <div class="contextmenu_item" @click="deleteFile">删除文件</div>
  <div class="contextmenu_item" @click="downLoadFile">下载文件</div>
  </div>
  
  <el-dialog width="30%" v-model="newDirForm.visible" title="新建目录">
    <el-form>
      <el-form-item label="新建目录" >  
        <el-input 
          rows=8 
          placeholder="请输入目录名" 
          v-model="newDirForm.name" 
          maxlength=20
          resize="vertical"
          autocomplete="off" />
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="newDirForm.visible = false">取消</el-button>
        <el-button type="primary" @click="newDir"
          >确认</el-button
        >
      </span>
    </template>
  </el-dialog>
  <el-dialog width="30%" v-model="newFileForm.visible" title="新建文件">
    <el-form :rules="rules">
      <el-form-item label="新建文件" >  
        <el-input 
          rows=8 
          placeholder="请输入文件名" 
          v-model="newFileForm.name" 
          maxlength=20
          resize="vertical"
          autocomplete="off" />
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="newFileForm.visible = false">取消</el-button>
        <el-button type="primary" @click="newFile"
          >确认</el-button
        >
      </span>
    </template>
  </el-dialog>

  <el-dialog
    title="上传文件"
    v-model="uploadForm.visible"
    width="30%"
    style = "height:20px; text-align: left; ">
    
    <el-upload
      class="upload-demo"
      :action="uploadURL()"
      :data="{dir:checkNode.path}"
      :on-success="handleUploadSucess"
      multiple
      :limit = "10"
      :before-upload="beforeUpload"
      :on-exceed="handleExceed"
      :on-error="handleFail"
      :file-list="uploadForm.fileList">
      <el-button  type="primary">点击上传</el-button>

      <template #tip>
        <div class="el-upload__tip">
          file size no more than 1M<br>file num no more than 10
        </div>
      </template>

    </el-upload>

    <template #footer>
    <span class="dialog-footer">
      <el-button @click="uploadForm.visible = false">取消</el-button>
      <el-button type="primary" @click="uploadForm.visible = false">确认</el-button>
    </span>
    </template>
  </el-dialog>

  <el-header style="width:100%">
    <div style="margin-left:20px width:100%">项目</div>
    
    <div>
      <el-button 
        style="margin-left:10px" 
        @click="checkNode = root;newFileForm.visible=true"
        circle>
        <el-icon><DocumentAdd/></el-icon>
      </el-button>
      <el-button 
        style="margin-left:10px" 
        @click="checkNode = root;newDirForm.visible=true"
        circle>
        <el-icon ><FolderAdd/></el-icon>
      </el-button>
      <el-button 
        style="margin-left:10px" 
        @click="checkNode = root;uploadForm.visible=true"
        circle>
        <el-icon><Upload/></el-icon>
      </el-button>

      <el-button 
        style="margin-left:10px" 
        @click="saveAll"
        circle>
        <el-icon><Check/></el-icon>
      </el-button>

      
      <el-button 
        style="margin-left:10px" 
        @click="getFileTree"
        circle>
        <el-icon><RefreshRight/></el-icon>
      </el-button>

    </div>

  </el-header>
  <el-main>
  <el-tree 
      class="file-tree"
      :data="fileTree" 
      node-key="id"
      empty-text=""
      :props="defaultProps" 
      @node-expand="(data,node,t)=>{data.isopen=true}"
      @node-click="handleNodeClick"
      @node-contextmenu="rightClick"
      :default-expanded-keys="defaultExpendNode"
      @node-collapse="(data,node,t)=>{data.isopen=false}">
  <template #default="{ node, data }">
  <span  class="custom-tree-node">
      <!--font-awesome-icon icon="fa-brands fa-java" /-->
        <el-icon v-if="data.children && data.isopen"><FolderOpened /></el-icon>
        <el-icon v-else-if="data.children && !data.isopen"><Folder/></el-icon>
        <el-icon v-else><Document /></el-icon>
      <i v-if="data.children && !data.isopen" class="el-icon-folder"></i>
      <i v-else-if="data.children && data.isopen" class="el-icon-folder-opened"></i>
      <i v-else class="el-icon-document"></i>
      <span>{{ node.label }}</span>
  </span>
  </template>
  </el-tree>
  </el-main>
</el-container>

</template>
 
<script>
import {Upload,
Delete,
DocumentAdd,
FolderAdd,
Folder,
FolderOpened,
Document,
Check,
RefreshRight,
} from '@element-plus/icons-vue';

import { useRouter } from "vue-router";
import { ref,toRefs,reactive, onMounted,onUnmounted } from 'vue'
import axios from 'axios'
import { ElMessage,ElMessageBox } from 'element-plus'
import eventBus from '@/assets/js/EventBus'


const defaultFileTree = [{id:0,label:'xiangmu',isopen:true,path:'/',children:
[
    {id:1,label:'dir1',isopen:false,path:'/1',children:[
        {id:2,label:'file1',path:'/2',isopen:false},
        {id:3,label:'file2',path:'/3',isopen:false},
        {id:4,label:'file3',isopen:false},
    ]},
    {id:5,label:'file4',path:'/4',isopen:false},
    {id:6,label:'file5',path:'/5',isopen:false},
    {id:7,label:'file6',path:'/6',isopen:false},
]}]
export default {
components:{
    Upload,
    Delete,
    DocumentAdd,
    FolderAdd,
    FolderOpened,
    Folder,
    Document,
    Check,
    RefreshRight,
},
  props: {
    pid:{
      type:Number,
      required:true,
      default:31
    },
    uid:{
      type:Number,
      required:true,
      default:31
    }
  },
setup(props){
    const router = useRouter();
    const fileTree = ref([]);
    const defaultExpendNode = ref([0]);
    const data = reactive({
    pid:props.pid,
    root :{id:0,label:'/',path:'/',isopen:false,children:fileTree.value},
    dialogTableVisible: false,
    TreeMenuVisible:false,
    FileMenuVisible:false,
    checkNode:null,
    newDirForm:{
        visible:false,
        name:'',
    },
    newFileForm:{
        visible:false,
        name:'',
    },
    uploadForm:{
      visible :false,
      name:'',
      fileList: [],
    },
    csrf_token:0,
    defaultProps: {
        children: 'children',
        label: 'label'
      },
    })
    const refresh = (data) => {
      //console.log("refresh",props.uid,data)
      if(true||props.uid != data.uid)
      {
        getFileTree();
        ElMessage.success(data.message)
      }        
    }
    //将isopen状态尽可能转移到在target中
    const mergeFileTree = (source,target,expendNode) => {
      let i = 0;
      for(let j = 0;j<target.length;++j)
      {
        while(i<source.length && source[i].label < target[j].label)
          i++;
        if(i<source.length 
          && source[i].label == target[j].label
          && source[i].children && target[j].children){
          target[j].isopen = source[i].isopen;
          if (target[j].isopen)
            expendNode.push(target[j].id)
          mergeFileTree(source[i].children,target[j].children,expendNode);
        }
      }
      return target
    }
    
    const saveAll = () => {
      eventBus.emit("saveAllFiles");
      //eventBus.emit('openfile',{label:label,path:path})
    }
    const openFile = (label,path) => {
      eventBus.emit('openfile',{label:label,path:path})
    }
    const downLoadFile = (name) => {
    axios.get(`/api/files/downloadfile/${data.pid}`,{params:{path:data.checkNode.path}})
    .then((response) => {
        let blob = new Blob([response.data])
        const utf8FilenameRegex = /filename\*=utf-8''([\w%\-.]+)(?:; ?|$)/i;
        const asciiFilenameRegex = /filename=(["']?)(.*?[^\\])\1(?:; ?|$)/i;
        
        let filename = 'download'
        const fileName = response.headers['content-disposition'];
        const utf8filename = utf8FilenameRegex.exec(fileName)
        const asciifilename = asciiFilenameRegex.exec(fileName)
        if (utf8filename)
          filename = utf8filename[1]
        else 
          filename = asciifilename[2]
        

        //console.log(fileName)
        let dom = document.createElement('a')
        let url = window.URL.createObjectURL(blob)
        dom.href = url
        dom.download = decodeURI(filename)
        
        dom.style.display = 'none'
        document.body.appendChild(dom)
        dom.click()
        dom.parentNode.removeChild(dom)
        window.URL.revokeObjectURL(url)
        ElMessage.success(name+'下载成功!');  
        }
    )}
    const beforeUpload = (file) => {
      let root = data.checkNode.id == 0 
                ? fileTree.value
                :data.checkNode.children
      //console.log(data.checkNode,root)
      
      for(let i = 0;i < root.length ;++i)
      {
          let childnode = root[i]
          console.log(childnode.name,data.newFileForm.name)
          if(childnode.label == data.newFileForm.name)
          {
              ElMessage.warning("文件"+childnode.label+"已经存在")
              return
          }
      }
      console.log("before",file)
      const isLt1M = file.size<1024*1024
      if(! isLt1M)
      {
        ElMessage.error("上传文件大小不超过1M")
        return false
      }
    }
    const handleUploadSucess = () => {
      data.uploadForm.fileList.shift()
      console.log("sucess",data.uploadForm.fileList)
      getFileTree()
    }
    const handleFail = (error) => {
      ElMessage.error("无权限，文件上传失败!")
    }
    const uploadURL = () => { return `/api/files/uploadfile/${data.pid}/` }
    const getFileTree = () => {
    axios.get(`api/files/filelist/${data.pid}/`)
    .then((response)=>{
        defaultExpendNode.value = [0]
        fileTree.value = mergeFileTree(fileTree.value,response.data.filelist,defaultExpendNode.value)

        //console.log("filetree",fileTree.value,defaultExpendNode.value)
    })
    .catch(function(error){
        console.log('error',error);
        if(error.response && error.response.status == 400)
            ElMessage.warning(error.response.data);
        else
            ElMessage.warning('未知错误')
        
    })
    }
    const newDir = ()=>{
        let root = data.checkNode.id == 0 
                  ? fileTree.value
                  :data.checkNode.children
        
        for(let i = 0;i<root.length;++i)
        {
            let childnode = root[i]
            if(childnode.label == data.newDirForm.name)
            {
                ElMessage.warning("目录"+childnode.label+"已经存在")
                return
            }
        }
          
        //let zhongpattern = new RegExp("[\u4E00-\u9FA5]+");
        //if(zhongpattern.test(data.newDirForm.name)){
        //  ElMessage.error('目录不能为中文') 
        //  return;
        //}
        let pattern = new RegExp('[\\\\/:*?\"<>|]');
        if(pattern.test(data.newDirForm.name)){
          ElMessage.error('目录不能包含【\\\\/:*?\"<>|】,请修改后重新上传!') 
          return;
        } 
        axios.post(`api/files/createdir/${data.pid}/`,
          {dir:data.checkNode.path,name:data.newDirForm.name},
        )
        .then((response) => {
            getFileTree()            
            data.newDirForm.visible = false
        })
        .catch(function (error) {
            console.log('error',error.response);
            if(error.response && error.response.status == 400)
                ElMessage.warning(error.response.data)
            else
                ElMessage.warning('未知错误')
        });
    }


    const newFile = ()=>{
        let root = data.checkNode.id == 0 
                  ? fileTree.value
                  :data.checkNode.children
        //console.log(data.checkNode,root)
        
        for(let i = 0;i<root.length;++i)
        {
            let childnode = root[i]
            console.log(childnode.name,data.newFileForm.name)
            if(childnode.label == data.newFileForm.name)
            {
                ElMessage.warning("文件"+childnode.label+"已经存在")
                return
            }
        }

        
        //let zhongpattern = new RegExp("[\u4E00-\u9FA5]+");
        //if(zhongpattern.test(data.newFileForm.name)){
        //  ElMessage.error('文件名不能包含中文') 
        //  return;
        //}

        let pattern = new RegExp('[\\\\/:*?\"<>|]');
        if(pattern.test(data.newFileForm.name)){
          ElMessage.error('文件名不能包含【\\\\/:*?\"<>|】,请修改后重新上传!') 
          return;
        } 

        axios.post(`api/files/createfile/${data.pid}/`,
          {dir:data.checkNode.path,name:data.newFileForm.name},
        )
        .then((response) => {
            getFileTree()            
            data.newFileForm.visible = false
        })
        .catch(function (error) {
            console.log('error',error.response);
            if(error.response && error.response.status == 400)
                ElMessage.warning(error.response.data);
            else
                ElMessage.warning('未知错误')
        });
    }
    const deleteDir = ()=>{
        axios.get(`api/files/removedir/${data.pid}/`,
          {params:{path:data.checkNode.path}}
        )
        .then((response) => {
            getFileTree()            
        })
        .catch(function (error) {
            console.log('error',error.response);
            if(error.response && error.response.status == 400)
                ElMessage.warning(error.response.data);
            else
                ElMessage.warning('未知错误')
        });
    }

  const deleteFile = ()=>{
        axios.get(`api/files/removefile/${data.pid}/`,
          {params:{path:data.checkNode.path}}
        )
        .then((response) => {
            getFileTree()  
        })
        .catch(function (error) {
            console.log('error',error.response);
            if(error.response && error.response.status == 400)
                ElMessage.warning(error.response.data);
            else
                ElMessage.warning('未知错误')
        });
  }
    const handleExceed = (files, fileList) => {
    ElMessage.warning(`当前限制选择 10 个文件，本次选择了 ${files.length} 个文件，共选择了 ${files.length + fileList.length} 个文件`);
    }
    const handleNodeClick = (data,checked,indeterminate) => {
    removeMenu();
    if(!data.children)
      openFile(data.label,data.path)
    //console.log('check',data)
    }
    onMounted(()=>{
      getFileTree();
      eventBus.on("refresh",refresh)
    })
    onUnmounted(() => {
      
      eventBus.off("refresh",refresh)
    })

    const rightClick = (event, node) => {
        //console.log('event',event)
        //console.log('node',node)
        data.checkNode = node
        //console.log('data.checknode',data.checkNode);
        removeMenu();
        if (node.children) { //for tree
            //this.currentData = data;
            data.TreeMenuVisible = false; // 先把模态框关死，目的是 第二次或者第n次右键鼠标的时候 它默认的是true
            data.TreeMenuVisible = true; // 显示模态窗口，跳出自定义菜单栏
        } else {
            //this.currentData = data;
            data.FileMenuVisible = false; // 先把模态框关死，目的是 第二次或者第n次右键鼠标的时候 它默认的是true
            data.FileMenuVisible = true; // 显示模态窗口，跳出自定义菜单栏
        }
        event.preventDefault(); //关闭浏览器右键默认事件,key就相当于event
        var menu = node.children?document.getElementById('treemenu'):
                        document.getElementById('filemenu');
        //console.log('mennu',menu)
        styleMenu(event,menu);
    }
    const removeMenu = () => {
        // 取消鼠标监听事件 菜单栏
        //console.log('removeTreeMenu')
        data.TreeMenuVisible = false;
        data.FileMenuVisible = false;
        document.removeEventListener("click", removeMenu); // 关掉监听，
    }

    const styleMenu = (key, menu) => {
        
        document.addEventListener("click", removeMenu); // 给整个document新增监听鼠标事件，点击任何位置执行foo方法
            
        menu.style.left = key.pageX  + "px";
        menu.style.top = key.pageY  + "px";
        //console.log('for menu style',menu.style.left,menu.style.top);
    }
    return {
        newDir,
        newFile,
        deleteFile,
        deleteDir,
        fileTree,
        defaultExpendNode,
        ...toRefs(data),
        handleExceed,
        handleNodeClick,
        rightClick,
        uploadURL,
        downLoadFile,
        handleUploadSucess,
        openFile,
        beforeUpload,
        saveAll,
        getFileTree,
        handleFail
    }
}
};

</script>
 
<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.box{
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: center;
}
.custom-tree-node{
  width:300px;
}
.el-header{
  padding:0;
}
.el-main{
  padding:0;
}
.file-tree{
  height:100%;
  width:auto;
}
.el-aside {
  
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: flex-start;
  color: rgb(192, 88, 88);
  background-color: rgb(172, 208, 150);
}
.menu {
  position: absolute;
  background-color: #fff;
  width: 100px;
  /*height: 106px;*/
  font-size: 12px;
  color: #444040;
  border-radius: 4px;
  -webkit-box-sizing: border-box;
  box-sizing: border-box;
  border-radius: 3px;
  border: 1px solid rgba(0, 0, 0, 0.15);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.175);
  white-space: nowrap;
  z-index: 1000;
}
.contextmenu_item {
  display: block;
  line-height: 34px;
  text-align: center;
}
.contextmenu_item:not(:last-child) {
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}
.contextmenu_item:hover {
  cursor: pointer;
  background: #66b1ff;
  border-color: #66b1ff;
  color: #fff;
}
</style>
