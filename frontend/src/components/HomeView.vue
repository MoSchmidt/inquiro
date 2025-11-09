<script setup>
import {useAuthStore} from "@/stores/auth.js";

const authStore = useAuthStore()

</script>

<template>
  <h1>Hello, {{ authStore.user }}</h1>
  <p>{{ authStore.accessToken }}</p>
</template>

<style scoped>

</style>