<template>
  <el-container>
    <el-header style="border-bottom: solid rgba(219, 219, 219, 0.874);">
      <Header :avatar="imageUrl"></Header>
    </el-header>
    <el-row>
      <el-col
      :span="9"
      :offset="3"
    >
    <div style="  display: flex;
      justify-content: center;
      align-items: center;
      margin-top:100px;">
      <el-card shadow="hover">
        <el-row
          style="
            justify-content: center;
            align-items: center;
            margin: 20px 0 0 0;
          "
        >
          
        </el-row>
        <el-row style="justify-content: center; align-items: center">
          <h2>上传头像</h2>
        </el-row>
        <el-row style="justify-content: center; align-items: center">
          <el-upload
            class="avatar-uploader"
            action="/api/accounts/uploadavatar/"
            :show-file-list="false"
            :on-error="handleError"
            :on-success="handleAvatarSuccess"
            :before-upload="beforeAvatarUpload">
            <img v-if="imageUrl" :src="imageUrl" class="avatar">
            <i v-else class="el-icon-plus avatar-uploader-icon"></i>
          </el-upload>
        </el-row>
      </el-card>
    </div>
    </el-col>

    <el-col
      :span="9"
      :offset="0"
    >
    <div style="  display: flex;
      justify-content: center;
      align-items: center;
      margin-top:100px; ">
    <el-card shadow="hover" >
     <el-row style="justify-content: center; align-items: center">
          <h2>修改密码</h2>
        </el-row>
        <el-form
          class="login-form"
          :model="model"
          :rules="rules"
          ref="form"
          @submit.native.prevent="resetPassword"
        >
          <el-form-item
            ><el-button
              type="success"
              class="login-button"
              style="margin-top: 0"
              round
              plain
              @click="verify()"
              :disabled="timeCnt != '验证邮箱'"
              >{{ timeCnt }}</el-button
            >
          </el-form-item>
          <el-form-item prop="verifyCode">
            <el-input
              v-model="model.verifyCode"
              placeholder="验证码"
              clearable
            ></el-input>
          </el-form-item>
          <el-form-item prop="password1">
            <el-input
              v-model="model.password1"
              placeholder="新密码"
              type="password"
              show-password
              clearable
            ></el-input>
          </el-form-item>
          <el-form-item prop="password2">
            <el-input
              v-model="model.password2"
              placeholder="确认新密码"
              type="password"
              show-password
              clearable
            ></el-input>
          </el-form-item>
          <el-form-item>
            <el-button
              :loading="loading"
              class="login-button"
              type="primary"
              native-type="submit"
              block
              >重置</el-button
            >
          </el-form-item>
        </el-form>
    </el-card>
    </div>
    </el-col>

    </el-row>
    
  </el-container>
</template>
 
<script>
import { ElMessage } from "element-plus";
import { Plus} from "@element-plus/icons-vue";
import Header from "../components/Header.vue";
export default {
  components:{Plus,Header},
  name: "register",
  data() {
    return {
      model: {
        password1: "",
        password2: "",
        verifyCode: "",
      },
      email:"",
      timeCnt: "验证邮箱",
      loading: false,
      imageUrl: '',
      uid:'',
      rules: {
        password1: [
          {
            required: true,
            message: "请输入密码",
            trigger: "blur",
          },
          {
            pattern: /^[_a-zA-Z0-9]{6,15}$/,
            message: "密码可包括英文字母、数字和下划线，6-15位",
            trigger: ["change", "blur"],
          },
        ],
        password2: [
          {
            required: true,
            message: "请确认密码",
            trigger: "blur",
          },
          {
            validator: (rule, value, callback) => {
              if (value !== this.model.password1) {
                callback(new Error("两次输入密码不一致"));
              } else {
                callback();
              }
            },
            trigger: ["blur", "change"],
          },
        ],
        verifyCode: [
          {
            required: true,
            message: "请输入验证码",
            trigger: "blur",
          },
        ],
      },
    };
  },
  created() {
    this.axios.get("/api/accounts/myinfo/", {}).then((response) => {
      this.email = response.data.data.email;
      this.uid= response.data.data.uid;
      this.imageUrl="/static/avatar/"+response.data.data.uid+`.jpg?${Date.now()}` ;
    });
  },
  methods: {
    verify() {
          this.axios
            .post("/api/accounts/forgetpassword1/", {
              email: this.email,
            })
            .then((response) => {
              if (response.data.message == "success") {
                ElMessage({
                  message: "Coconow已向您的邮箱发送验证码，请查收",
                  type: "success",
                });
                let seconds = 60;
                this.timeCnt = `${seconds}秒后重发`;
                let timer = setInterval(() => {
                  seconds--;
                  this.timeCnt = `${seconds}秒后重发`;
                  if (seconds == 0) {
                    clearInterval(timer);
                    this.timeCnt = "验证邮箱";
                  }
                }, 1000);
              } else {
                ElMessage({
                  message: response.data.data.detail,
                  type: "error",
                });
              }
      });
    },
    handleError(err){
      console.log(err,err.method,typeof err);
    },
    handleAvatarSuccess(res, file) {
        this.imageUrl = URL.createObjectURL(file.raw);
        this.$message({
              message: '更改头像成功!',
              type: 'success'
            });
        //this.$router.push({ name: "UserSpace" });
    },
    beforeAvatarUpload(file) {
        const isJPG = file.type === 'image/jpeg';
        const isLt2M = file.size / 1024 / 1024 < 2;

        if (!isJPG) {
          this.$message.error('上传头像图片只能是 JPG 格式!');
        }
        if (!isLt2M) {
          this.$message.error('上传头像图片大小不能超过 2MB!');
        }
        return isJPG && isLt2M;
      },
    resetPassword() {
      this.$refs["form"].validate((isValid) => {
        if (!isValid) {
          ElMessage({
            message: "请检查输入",
            type: "error",
          });
        } else {
          this.axios
            .post("/api/accounts/forgetpassword2/", {
              password: this.model.password1,
              email: this.email,
              verify_code: this.model.verifyCode,
            })
            .then((response) => {
              if (response.data.message == "success") {
                ElMessage({
                  message: "密码已重置",
                  type: "success",
                });
                this.$router.push("/Login");
              } else {
                ElMessage({
                  message: response.data.data.detail,
                  type: "error",
                });
              }
            })
            .catch(function (error) {
              console.log(error);
            });
        }
      });
    },
  },
};
</script>
 
<style scoped>
.login {
  width: 100%;
  height: 100%;
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  position: absolute;
}

.login-button {
  width: 100%;
  margin-top: 20px;
}
.login-form {
  width: 250px;
}
.forgot-password {
  margin-top: 10px;
}
</style>
<style lang="scss">
$teal: rgb(0, 124, 137);
.el-button--primary {
  background: $teal;
  border-color: $teal;

  &:hover,
  &.active,
  &:focus {
    background: lighten($teal, 7);
    border-color: lighten($teal, 7);
  }
}
.login .el-input__inner:hover {
  border-color: $teal;
}
.login .el-input__prefix {
  background: rgb(238, 237, 234);
  left: 0;
  height: calc(100% - 2px);
  left: 1px;
  top: 1px;
  border-radius: 3px;
  .el-input__icon {
    width: 30px;
  }
}
.login .el-input input {
  padding-left: 10px;
}
.login .el-card {
  padding-top: 0;
  padding-bottom: 30px;
}
h2 {
  font-family: "Open Sans";
  letter-spacing: 1px;
  font-family: Roboto, sans-serif;
  padding-bottom: 20px;
}
a {
  color: $teal;
  text-decoration: none;
  &:hover,
  &:active,
  &:focus {
    color: lighten($teal, 7);
  }
}
.login .el-card {
  width: 340px;
  display: flex;
  justify-content: center;
}
</style>

<style>
  .avatar-uploader .el-upload {
    border: 1px dashed #d9d9d9;
    border-radius: 6px;
    cursor: pointer;
    position: relative;
    overflow: hidden;
  }
  .avatar-uploader .el-upload:hover {
    border-color: #409EFF;
  }
  .avatar-uploader-icon {
    font-size: 28px;
    color: #8c939d;
    width: 178px;
    height: 178px;
    line-height: 178px;
    text-align: center;
  }
  .avatar {
    width: 178px;
    height: 178px;
    display: block;
  }
</style>