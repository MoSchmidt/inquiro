<script setup lang="ts">
import {useAuthStore} from "@/stores/auth";

const authStore = useAuthStore()

</script>

<template>
  <h1>Hello, {{ authStore.user }}</h1>
  <p>{{ authStore.accessToken }}</p>
</template>

<style scoped>

</style>