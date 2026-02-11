<script setup lang="ts">
import { ref } from "vue"
import Login from "./views/Login.vue"
import Upload from "./views/Upload.vue"
import Admin from "./views/Admin.vue"

const isAuth = ref(localStorage.getItem("auth") === "true")
const currentView = ref('upload')

// Die Funktion für den geschützten Zugriff
const tryAccessAdmin = () => {
  const password = prompt("Bitte Admin-Passwort eingeben:")
  
  // Ersetze 'dein-geheimes-passwort' mit deinem Wunsch-Passwort
  if (password === 'v3rs0rgungchange!') { 
    currentView.value = 'admin'
  } else {
    alert("Falsches Passwort!")
  }
}

const handleLoginSuccess = () => {
  isAuth.value = true
}
</script>

<template>
  <div v-if="!isAuth">
    <Login @login-success="handleLoginSuccess" />
  </div>

  <div v-else>
    <Upload 
      v-if="currentView === 'upload'" 
      @go-to-admin="tryAccessAdmin" 
    />

    <Admin 
      v-else-if="currentView === 'admin'" 
      @go-to-upload="currentView = 'upload'" 
    />
  </div>
</template>