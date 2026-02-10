<script setup lang="ts">
import { ref } from "vue"

const password = ref("")
const error = ref(false)

function login() {
  if (password.value === "v3rs0rgung!") {
    localStorage.setItem("auth", "true")
    location.reload()
  } else {
    error.value = true
  }
}
</script>

<template>
  <div class="min-h-screen bg-slate-950 flex items-center justify-center text-slate-100">
    <div class="w-full max-w-sm bg-slate-900 rounded-2xl p-8 shadow-xl">

      <!-- Header -->
      <div class="mb-8 text-center">
        <h1 class="text-2xl font-semibold tracking-tight">
          PDF Generator
        </h1>
        <p class="text-sm text-slate-400 mt-1">
          Versorgungsvereinbarung erstellen
        </p>
      </div>

      <!-- Input -->
      <div class="mb-4">
        <input
          v-model="password"
          type="password"
          placeholder="Passwort"
          class="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-3
                 placeholder-slate-500 focus:outline-none
                 focus:ring-2 focus:ring-cyan-400 transition"
        />
      </div>

      <!-- Button -->
      <button
        @click="login"
        class="w-full bg-cyan-400 text-black py-3 rounded-xl font-medium
               hover:bg-cyan-300 transition"
      >
        Login
      </button>

      <!-- Error -->
      <p
        v-if="error"
        class="text-red-400 text-sm mt-4 text-center"
      >
        Falsches Passwort
      </p>

    </div>
  </div>
</template>
