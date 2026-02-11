<script setup lang="ts">
import { ref } from "vue"

const file = ref<File | null>(null)
const loading = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)

const baseUrl =
  import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000"

function openExplorer() {
  fileInput.value?.click()
}

function onDrop(e: DragEvent) {
  e.preventDefault()

  const droppedFiles = e.dataTransfer?.files

  if (!droppedFiles || droppedFiles.length === 0) {
    file.value = null
    return
  }

  const firstFile = droppedFiles.item(0)
  file.value = firstFile ?? null
}

function onFileSelected(e: Event) {
  const target = e.target as HTMLInputElement | null

  if (!target?.files || target.files.length === 0) {
    file.value = null
    return
  }

  const firstFile = target.files.item(0)
  file.value = firstFile ?? null
}

function removeFile(e: Event) {
  e.stopPropagation()
  file.value = null

  if (fileInput.value) {
    fileInput.value.value = ""
  }
}

async function upload() {
  const selectedFile = file.value

  if (!selectedFile) {
    alert("Bitte zuerst eine Excel-Datei auswählen")
    return
  }

  loading.value = true

  try {
    const form = new FormData()
    form.append("file", selectedFile)

    const cleanUrl = baseUrl.replace(/\/$/, "")

    const res = await fetch(`${cleanUrl}/upload`, {
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

    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)

    // Optional: Reset nach erfolgreichem Upload
    file.value = null
    if (fileInput.value) {
      fileInput.value.value = ""
    }
  } catch (error) {
    console.error(error)
    alert("Download fehlgeschlagen")
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div
    class="min-h-screen bg-slate-950 text-slate-100 flex items-center justify-center relative"
  >
    <div class="absolute top-6 right-6 z-50">
      <button
        @click="$emit('go-to-admin')"
        class="bg-slate-800 hover:bg-slate-700 text-slate-300 px-4 py-2 rounded-lg text-sm border border-slate-700 transition"
      >
        Admin Panel
      </button>
      </div>

      <div class="min-h-screen bg-slate-950 text-slate-100 flex items-center justify-center relative">
     </div>

    <div
      class="w-full max-w-2xl bg-slate-900 rounded-2xl p-8 shadow-xl"
    >
      <h1 class="text-3xl font-semibold mb-8 text-center">
        Versorgungsvereinbarung erstellen
      </h1>

      <p class="text-sm text-slate-400 mb-6 text-center">
        <a
          :href="`${baseUrl}/template`"
          class="hover:text-cyan-400 underline underline-offset-4"
        >
          Template Sheet Download
        </a>
      </p>

      <div
        class="border-2 border-dashed border-slate-700 rounded-xl p-10 text-center
               hover:border-cyan-400 transition mb-6 cursor-pointer relative"
        @drop.prevent="onDrop"
        @dragover.prevent
        @click="openExplorer"
      >
        <input
          type="file"
          ref="fileInput"
          class="hidden"
          accept=".xlsx,.xls"
          @change="onFileSelected"
        />

        <div v-if="!file">
          <p class="text-slate-400">
            Excel-Datei hier ablegen oder anklicken
          </p>
        </div>

        <div
          v-else
          class="flex items-center justify-center gap-3"
        >
          <p class="text-cyan-400 font-medium">
            {{ file.name }}
          </p>

          <button
            @click.stop="removeFile"
            class="text-slate-500 hover:text-red-400 transition-colors text-xl font-bold p-1"
          >
            ×
          </button>
        </div>
      </div>

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
