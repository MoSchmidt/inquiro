import { ref } from 'vue';

export function useFileSelection(initialFile: File | null = null) {
  const fileInput = ref<HTMLInputElement | null>(null);
  const selectedFile = ref<File | null>(initialFile);

  const triggerFileSelect = () => {
    fileInput.value?.click();
  };

  const handleFileChange = (event: Event) => {
    const target = event.target as HTMLInputElement;
    // We only allow a single file to be selected
    if (target.files && target.files[0]) {
      selectedFile.value = target.files[0];
    }
  };

  const removeFile = () => {
    selectedFile.value = null;
    if (fileInput.value) {
      fileInput.value.value = '';
    }
  };

  return {
    fileInput,
    selectedFile,
    triggerFileSelect,
    handleFileChange,
    removeFile,
  };
}