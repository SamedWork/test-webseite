<script setup lang="ts">
import { ref } from "vue"

const emit = defineEmits(['go-to-upload'])

const pdfFile = ref<File | null>(null)
const uploading = ref(false)
const baseUrl = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000"

async function saveGlobalPdf() {
  if (!pdfFile.value) return
  uploading.value = true
  
  const form = new FormData()
  form.append("pdf", pdfFile.value)

  try {
    const res = await fetch(`${baseUrl}/admin/upload-pdf`, {
      method: "POST",
      body: form
    })
    if (res.ok) alert("PDF global gespeichert!")
    else alert("Fehler beim Speichern")
  } catch (e) {
    alert("Server nicht erreichbar")
  } finally {
    uploading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen bg-slate-950 text-white flex flex-col items-center justify-center p-12 relative">
    
    <div class="absolute top-8 left-8">
      <button 
        @click="emit('go-to-upload')" 
        class="text-cyan-400 hover:underline bg-transparent border-none cursor-pointer"
      >
        ← Zurück
      </button>
    </div>

    <div class="w-full max-w-lg">
      <h1 class="text-2xl font-bold mb-8 text-center">Admin Panel: Globales PDF Management</h1>
      
      <div class="bg-slate-900 p-8 rounded-xl border border-slate-800 shadow-xl">
        <label class="block mb-4 text-slate-400">Neues globales PDF hochladen:</label>
        
        <input 
          type="file" 
          accept="application/pdf"
          @change="(e: any) => pdfFile = e.target.files[0]"
          class="block w-full text-sm text-slate-400 
                 file:mr-4 file:py-2 file:px-4 
                 file:rounded-full file:border-0 
                 file:text-sm file:font-semibold 
                 file:bg-cyan-400 file:text-black 
                 hover:file:bg-cyan-300 mb-6"
        />

        <button 
          @click="saveGlobalPdf"
          :disabled="!pdfFile || uploading"
          class="w-full bg-white text-black py-2 rounded-lg font-bold disabled:opacity-50 transition-opacity"
        >
          {{ uploading ? "Speichert..." : "PDF im Backend ersetzen" }}
        </button>
      </div>
    </div>
  </div>
</template>