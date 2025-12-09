<script setup lang="ts">
import { computed, ref } from 'vue'
import { useAuthStore } from '@/stores/auth'

const props = defineProps<{ open: boolean }>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'create', payload: { name: string; email: string; password: string }): void
}>()

const dialogOpen = computed({
  get: () => props.open,
  set: (value: boolean) => {
    if (!value) emit('close')
  },
})


const name = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const error = ref<string | null>(null)
const loading = ref(false)

const authStore = useAuthStore()


const resetForm = () => {
  name.value = ''
  email.value = ''
  password.value = ''
  confirmPassword.value = ''
  error.value = null
}


const submit = async () => {
  error.value = null

  // UI-level validation
  if (password.value !== confirmPassword.value) {
    error.value = 'Passwords do not match'
    return
  }

  if (password.value.length < 8) {
    error.value = 'Password must be at least 8 characters long'
    return
  }

  loading.value = true

  try {
    const username = email.value || name.value
    await authStore.signup(username, password.value)

    emit('create', {
      name: name.value,
      email: email.value,
      password: password.value,
    })

    resetForm()
    dialogOpen.value = false
  } catch (err: unknown) {
    error.value =
      // axios-style
      // @ts-expect-error
      err?.response?.data?.detail ||
      (err as Error)?.message ||
      'Signup failed'
  } finally {
    loading.value = false
  }
}
</script>
