<template>
  <el-container>
    <el-header style="border-bottom: solid rgba(219, 219, 219, 0.874);">
      <Header
        :avatar="imageUrl"
      ></Header>
    </el-header>

  
  </el-container>
   <div>
    <el-dialog
      :append-to-body="true"
      v-if="dialogCreateVisible"
      title="新建项目"
      v-model="dialogCreateVisible"
      width="25%"
      :center="true"
    >
      <el-input
        v-model="Pname"
        placeholder="请输入项目名称，不支持中文"
        style="width: full;margin-left 10px;margin-right:10px;"
      ></el-input
      ><br />
      <div slot="footer" class="dialog-footer" style="margin-top:15px;">
        <el-button @click="dialogCreateVisible = false">取消</el-button>
        <el-button type="primary" @click="createProject()">确认</el-button>
      </div>
    </el-dialog>
  </div>
  <div style="margin-left: 200px;margin-top :30px;">
    <el-button @click="dialogCreateVisible = true" type="success">
      <el-icon><FolderAdd /></el-icon>
      新建项目
   </el-button>
  </div>
  <div
    class="demo-collapse"
    style="margin-top: 30px; margin-left: 150px; margin-right :150px;"
  >
    <el-collapse  accordion>
      <div v-for="(project, index) in this.project_list" v-bind:key="index">
        <el-collapse-item v-bind:title="project['pname']" v-bind:name="index">
          <el-descriptions
            title="项目详情"
            :column="3"
            border
          >
            <template #extra>
              <div>
              <div v-if="project['privilege'] == 'owner'">
                <el-button
                  type="danger"
                  @click="dialogDeleteVisible[index] = true"
                  >删除项目</el-button
                >
              </div>
              </div>
              <div>
                <el-dialog
                  :append-to-body="true"
                  v-if="dialogDeleteVisible[index]"
                  title="Delete Project"
                  v-model="dialogDeleteVisible[index]"
                  width="25%"
                  :center="true"
                >
                  <el-input
                    v-model="Pname"
                    placeholder="请输入项目名称以确认删除"
                    style="width: full;margin-left 10px;margin-right:10px;"
                  ></el-input
                  ><br />
                  <div slot="footer" class="dialog-footer" style="margin-top:15px;">
                    <el-button @click="dialogDeleteVisible[index] = false"
                      >取消</el-button
                    >
                    <el-button
                      type="primary"
                      @click="deleteProject(index)"
                      :id="forId(index)"
                      >确认</el-button
                    >
                  </div>
                </el-dialog>
              </div>
            </template>
            <el-descriptions-item label="进入项目">
              <el-button type="text" @click="jumpHome(index)">
                {{ project["pname"] }}
              </el-button>
            </el-descriptions-item>
            <el-descriptions-item label="权限" :span="2">
              <el-tag size="small">{{ project["privilege"] }}</el-tag>
            </el-descriptions-item>

            <el-descriptions-item label="项目成员">
              <div
                v-for="(group, index3) in this.group_list"
                v-bind:key="index3"
              >
                <div v-if="group['pid'] == project['pid']">
                  <div
                    v-for="(member, index2) in group['membermsg']"
                    v-bind:key="index2"
                  >
                    <el-tooltip
                      class="box-item"
                      effect="light"
                      v-bind:content="member['username']"
                      placement="top-start"
                    >
                      <div style="float: left; margin-left: 5px">
                        <el-avatar :size="50" :src="getAvatar(member['id'])"></el-avatar>
                      </div>
                    </el-tooltip>
                  </div>
                </div>
              </div>
              <div style="float: left; margin-left: 5px">
                <div>
                  <div v-if="project['privilege'] == 'owner'">
                    <el-avatar
                      :size="50"
                      @click="dialogInviteVisible[index] = true"
                    >
                      <img src="../assets/addUser.png" alt="logo" />
                    </el-avatar>
                  </div>
                  <el-dialog
                    :append-to-body="true"
                    v-if="dialogInviteVisible[index]"
                    title="邀请用户"
                    v-model="dialogInviteVisible[index]"
                    width="25%"
                    :center="true"
                  >
                    <el-input
                      v-model="Username"
                      placeholder="请输入用户名"
                      style="width: full;margin-left 10px;margin-right:10px;"
                    ></el-input
                    ><br />
                    <div slot="footer" class="dialog-footer" style="margin-top:15px;">
                      <el-button @click="dialogInviteVisible[index] = false"
                        >取消</el-button
                      >
                      <el-button
                        type="primary"
                        @click="inviteUser(index)"
                        :id="forId(index)"
                        >邀请</el-button
                      >
                    </div>
                  </el-dialog>
                </div>
              </div>
              <div style="float: left; margin-left: 5px">
                <div v-if="project['privilege'] == 'owner'">
                  <el-avatar
                    :size="50"
                    @click="dialogRemoveVisible[index] = true"
                    ><img src="../assets/removeUser.png" alt="logo" />
                  </el-avatar>
                </div>
                <div>
                  <el-dialog
                    :append-to-body="true"
                    v-if="dialogRemoveVisible[index]"
                    title="移除用户"
                    v-model="dialogRemoveVisible[index]"
                    width="25%"
                    :center="true"
                  >
                    <el-input
                      v-model="Username"
                      placeholder="please input Username"
                      style="width: full;margin-left 10px;margin-right:10px;"
                    ></el-input
                    ><br />
                    <div slot="footer" class="dialog-footer" style="margin-top:15px;">
                      <el-button @click="dialogRemoveVisible[index] = false"
                        >取消</el-button
                      >
                      <el-button
                        type="primary"
                        @click="removeUser($event)"
                        :id="forId(index)"
                        >移除</el-button
                      >
                    </div>
                  </el-dialog>
                </div>
              </div>
            </el-descriptions-item>
          </el-descriptions>
        </el-collapse-item>
      </div>
    </el-collapse>
  </div>
  <el-carousel
      indicator-position="outside"
      style="margin-top: 100px; margin: 0 auto; width: 432px"
      height="300px"
    >
      <el-carousel-item v-for="item in 2" :key="item">
        <img src="../assets/project_logo.png" alt="logo" style="width: 100%;height: 100%;" />
      </el-carousel-item>
    </el-carousel>
</template>
  
<script >
import Header from "../components/Header.vue";
import { ElMessageBox } from "element-plus";
import { ArrowDown } from "@element-plus/icons-vue";
import { WarningFilled } from "@element-plus/icons-vue";
import { CirclePlus, Plus, Minus,FolderAdd } from "@element-plus/icons-vue";
import { reactive, toRefs } from "vue";
import { Check } from "@element-plus/icons-vue";
import Cookies from 'js-cookie'

export default {
  components: {
    Minus,
    Plus,
    Check,
    FolderAdd,
    reactive,
    toRefs,
    CirclePlus,
    WarningFilled,
    ArrowDown,
    ElMessageBox,
    Header,
  },
  el: "#app",
  name: "userspace",
  data() {
    return {
      uid: "",
      email: "132",
      project_list: [],
      pids: [],
      pnames: [],
      privileges: [],
      group_list: [],
      myname:'',
      Username: "",
      dialogInviteVisible: [],
      dialogRemoveVisible: [],
      dialogDeleteVisible: [],
      dialogCreateVisible: false,
      formLabelWidth: "90px",
      Pname: "",
      imageUrl:"",
    };
  },
  created() {
    this.axios.get("/api/accounts/myinfo/", {}).then((response) => {
      this.email = response.data.data.email;
      this.project_list = response.data.data.projects;
      this.uid = response.data.data.uid;
      this.myname = response.data.data.username;
      this.imageUrl="/static/avatar/"+this.uid+".jpg"+ `?${Date.now()}`
      var i;
      for (i = 0; i < this.project_list.length; i++) {
        this.pnames.push(this.project_list[i]["pname"]);
        this.pids.push(this.project_list[i]["pid"]);
        this.privileges.push(this.project_list[i]["privileges"]);
        this.dialogInviteVisible.push(false);
        this.dialogRemoveVisible.push(false);
        this.dialogDeleteVisible.push(false);
      }
      for (i = 0; i < this.project_list.length; i++) {
        this.axios
          .get("/api/projects/info/".concat(this.pids[i]), {})
          .then((response) => {
            this.group_list.push(response.data);
          });
      }
    });
  },
  methods: {
    forId: function (index) {
      return index;
    },
    jumpHome: function (param1) {
      let number = param1;
      let pid = this.project_list[number]["pid"];
      Cookies.set("uid",this.uid)
      
      this.$router.push({ name: "Home", query: { pid: pid } });
    },

    getAvatar:function(param1){
      let src="/static/avatar/"+param1+".jpg" + `?${Date.now()}`;
      return src;
    },

    inviteUser: function (param1) {
      let number = param1;

      this.axios
        .post("/api/projects/inviteuser/", {
          pid: this.project_list[number]["pid"],
          invitename: this.Username,
        })
        .then((response) => {
          let res = eval(response);
          let msg = response.data.message;
          if(msg!="success"){
            this.$message({
            message: response.data.data.detail,
            type: 'error'
          });
            return;
          }
          this.$message({
            message: '邀请成员成功！',
            type: 'success'
          });
          this.dialogInviteVisible[param1] = false;
          this.group_list=[];
          var i;
          for (i = 0; i < this.project_list.length; i++) {
        this.axios
          .get("/api/projects/info/".concat(this.pids[i]), {})
          .then((response) => {
            this.group_list.push(response.data);
          });
      }
        })
        .catch(function (error) {
          console.log(error);
        });
    },

    removeUser: function (param1) {
      let number = param1.currentTarget.id;
      if(this.Username==this.myname){
        this.$message({
            message: '不能移除项目拥有者！',
            type: 'error'
          });
        return;
      }
      this.axios
        .post("/api/projects/removeuser/", {
          pid: this.project_list[number]["pid"],
          username: this.Username,
        })
        .then((response) => {
          this.dialogRemoveVisible[number] = false;
          this.group_list=[];
          this.$message({
            message: '移除成员成功！',
            type: 'success'
          });
          
          var i;
          for (i = 0; i < this.project_list.length; i++) {
        this.axios
          .get("/api/projects/info/".concat(this.pids[i]), {})
          .then((response) => {
            this.group_list.push(response.data);
          });
          }
        })
        .catch(function (error) {
          console.log(error);
        });
    },

    deleteProject: function (param1) {
      let number = param1;
      if (this.project_list[number]["pname"] != this.Pname) {
        this.$message({
            message: "Project Name Doesn't Match!",
            type: 'error'
          });
      } else {
        this.axios
          .delete("/api/projects/remove/", {
            params: {
              pid: this.project_list[number]["pid"],
            },
          })
          .then((response) => {
            this.$message({
              message: '删除项目成功！',
              type: 'success'
            });
            this.dialogDeleteVisible = false;
            
            this.axios.get("/api/accounts/myinfo/", {}).then((response) => {
      this.email = response.data.data.email;
      this.project_list = response.data.data.projects;
      this.uid = response.data.data.uid;
      var i;
      this.pnames=[];
      this.pids=[];
      this.privileges=[];
      this.dialogInviteVisible=[];
      this.dialogRemoveVisible=[];
      this.dialogDeleteVisible=[];
      for (i = 0; i < this.project_list.length; i++) {
        this.pnames.push(this.project_list[i]["pname"]);
        this.pids.push(this.project_list[i]["pid"]);
        this.privileges.push(this.project_list[i]["privileges"]);
        this.dialogInviteVisible.push(false);
        this.dialogRemoveVisible.push(false);
        this.dialogDeleteVisible.push(false);
      }
      this.group_list=[];
      for (i = 0; i < this.project_list.length; i++) {
        this.axios
          .get("/api/projects/info/".concat(this.pids[i]), {})
          .then((response) => {
            this.group_list.push(response.data);
          });
      }
    });
          })
          .catch(function (error) {
            console.log(error);
          });
      }
    },

    createProject: function () {
      if(this.Pname.length>15){
        this.$message({
              message: '项目名最大长度是15！',
              type: 'error'
            });
        return;
      }
      if(this.Pname.length<2){
        this.$message({
              message: '项目名最小长度是2！',
              type: 'error'
            });
        return;
      }
      let pattern = new RegExp("[\u4E00-\u9FA5]+");
      if(pattern.test(this.Pname)){
        this.$message({
              message: '项目名不支持中文！',
              type: 'error'
            });
        return;
      }
      pattern = new RegExp("[a-zA-Z0-9][a-zA-Z0-9_.-]+");
      if(!pattern.test(this.Pname)){
        this.$message({
              message: '项目名只支持数字、字母！',
              type: 'error'
            });
        return;
      }

      this.axios
        .post("/api/projects/create/", {
          pname: this.Pname,
        })
        .then((response) => {
          if (response.data.message == "success") {
            this.dialogCreateVisible = false;
            this.$message({
              message: '创建成功！',
              type: 'success'
            });
            this.axios.get("/api/accounts/myinfo/", {}).then((response) => {
      this.email = response.data.data.email;
      this.project_list = response.data.data.projects;
      this.uid = response.data.data.uid;
      var i;
      this.pnames=[];
      this.pids=[];
      this.privileges=[];
      this.dialogInviteVisible=[];
      this.dialogRemoveVisible=[];
      this.dialogDeleteVisible=[];
      for (i = 0; i < this.project_list.length; i++) {
        this.pnames.push(this.project_list[i]["pname"]);
        this.pids.push(this.project_list[i]["pid"]);
        this.privileges.push(this.project_list[i]["privileges"]);
        this.dialogInviteVisible.push(false);
        this.dialogRemoveVisible.push(false);
        this.dialogDeleteVisible.push(false);
      }
      this.group_list=[];
      for (i = 0; i < this.project_list.length; i++) {
        this.axios
          .get("/api/projects/info/".concat(this.pids[i]), {})
          .then((response) => {
            this.group_list.push(response.data);
          });
      }
    });
          } else {
            this.$message({
            message: response.data.data.detail,
            type: 'error'
          });
          }
        })
        .catch(function (error) {
          console.log(error);
        });
    },
  },
};
</script>
 
<style scoped>
.box {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: center;
}
.el-collapse {
  margin-right: 50px;
  margin-left: 50px;
}
.el-descriptions {
  margin-top: 20px;
  margin-right: 70px;
  margin-left: 70px;
}
/deep/ .el-collapse-item__header {
  font-size: 20px;
}
.el-carousel__item h3 {
  display: flex;
  color: #475669;
  opacity: 0.75;
  line-height: 300px;
  margin: 0;
}

.el-carousel__item:nth-child(2n) {
  background-color: #99a9bf;
}

.el-carousel__item:nth-child(2n + 1) {
  background-color: #d3dce6;
}
</style>  