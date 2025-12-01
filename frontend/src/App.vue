<script setup lang="ts">
import { ref } from 'vue';
import CreateAccount from './components/CreateAccount.vue';
import { useAuthStore } from './stores/auth';

const showCreateAccount = ref(false);
const auth = useAuthStore();
</script>

<template>
  <div>
    <header style="padding:12px;border-bottom:1px solid #e5e7eb;background:#fff;display:flex;justify-content:flex-end;">
      <button v-if="!auth.isAuthenticated" @click="showCreateAccount = true" style="padding:8px 12px;border:1px solid #3b82f6;color:#3b82f6;background:transparent;border-radius:6px;">Create Account</button>
      <span v-else style="padding:8px 12px;color:#10b981">Logged in</span>
    </header>

    <main>
      <router-view />
    </main>

    <CreateAccount :open="showCreateAccount" @close="showCreateAccount = false" />
  </div>
</template>

<style scoped></style>
