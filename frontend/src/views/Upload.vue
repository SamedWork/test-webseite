<script setup lang="ts">
import { ref } from "vue"

const file = ref<File | null>(null)
const loading = ref(false)

function onDrop(e: DragEvent) {
  e.preventDefault()
  file.value = e.dataTransfer?.files[0] ?? null
}

async function upload() {
  if (!file.value) {
    alert("Bitte zuerst eine Excel-Datei auswählen")
    return
  }
  loading.value = true

  try {
    const form = new FormData()
    form.append("file", file.value)

    // ÄNDERUNG HIER: Nutze die Umgebungsvariable oder einen Fallback
    const baseUrl = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000"
    
    const res = await fetch(`${baseUrl}/upload/`, { // Endslash beachten, falls im Backend so definiert
      method: "POST",
      body: form,
    })

    if (!res.ok) {
      throw new Error(`HTTP ${res.status}`)
    }

    const blob = await res.blob()

    const url = window.URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = "result.zip"
    document.body.appendChild(a)
    a.click()
    a.remove()
    window.URL.revokeObjectURL(url)

  } catch (e) {
    alert("Download fehlgeschlagen")
  } finally {
    loading.value = false
  }
}



</script>

<template>
  <div class="min-h-screen bg-slate-950 text-slate-100 flex items-center justify-center">
    <div class="w-full max-w-2xl bg-slate-900 rounded-2xl p-8 shadow-xl">

      <h1 class="text-3xl font-semibold mb-8 text-center">
        Versorgungsvereinbarung erstellen
      </h1>
        <p class="text-sm text-slate-400 mb-6 text-center">
            <a
                href="http://127.0.0.1:8000/template"
                class="hover:text-cyan-400 underline underline-offset-4"
            >
                Template Sheet Download
            </a>
        </p>
      <!-- Dropzone -->
      <div
        class="border-2 border-dashed border-slate-700 rounded-xl p-10 text-center
               hover:border-cyan-400 transition mb-6 cursor-pointer"
        @drop="onDrop"
        @dragover.prevent
      >
        <p v-if="!file" class="text-slate-400">
          Excel-Datei hier ablegen
        </p>
        <p v-else class="text-cyan-400 font-medium">
          {{ file.name }}
        </p>
      </div>

      <!-- Button -->
      <button
        @click="upload"
        :disabled="loading"
        class="w-full bg-cyan-400 text-black py-3 rounded-xl font-semibold
               hover:bg-cyan-300 transition disabled:opacity-50"
      >
        {{ loading ? "Verarbeitung läuft..." : "Upload starten" }}
      </button>

    </div>
  </div>
</template>
