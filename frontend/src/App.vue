<script setup lang="ts">
import Login from "./views/Login.vue"
import Upload from "./views/Upload.vue"

const isAuth = localStorage.getItem("auth") === "true"
</script>

<template>
  <Login v-if="!isAuth" />
  <Upload v-else />
</template>
