
<template>
  <router-view />
</template>

<script setup>
import Header from "@/components/Header.vue";
</script>

<style lang="scss" scoped>
.el-header {
  background-color: #545c64;
}
.el-aside {
  background-color: #111;
}
.el-footer {
  background-color: #300;
}
.el-main {
  padding-top: 0;
}
</style>