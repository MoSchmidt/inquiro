<script setup lang="ts">
import { ref, watch } from 'vue';
import { VList, VListItem, VListItemTitle, VListItemSubtitle, VDivider, VBtn, VIcon, VCard, VTextField, VDialog, VCardActions, VCardText, VCardTitle } from 'vuetify/components';
import { X, LogOut, FolderOpen, Clock, LogIn, Plus, AlertCircle, CheckCircle } from 'lucide-vue-next';
import { Project } from './types'; // Importiere den Typ

const props = defineProps<{
  isOpen: boolean;
  recentProjects: Project[];
  isLoggedIn: boolean;
}>();

const emit = defineEmits([
  'close',
  'projectSelect',
  'newProject',
  'login',
  'logout',
]);

const username = ref('')
//const email = ref('');
//const password = ref('');
const loginDialogOpen = ref(false);

const handleLoginSubmit = () => {
  if (username.value) {
    emit('login', username.value);
    username.value = '';
    loginDialogOpen.value = false;
  }
  /*
  if (email.value && password.value) {
    emit('login', email.value, password.value);
    email.value = '';
    password.value = '';
    loginDialogOpen.value = false;
  }
   */
};

const handleNewProjectClick = () => {
  emit('newProject');
  emit('close');
}
</script>

<template>
  <div class="d-flex flex-column h-100">
    <v-card flat class="pa-4 d-flex align-center justify-space-between border-b-sm">
      <h2 class="text-h6">Menü</h2>
      <v-btn icon variant="text" @click="emit('close')">
        <v-icon :icon="X" size="24" />
      </v-btn>
    </v-card>

    <div class="flex-grow-1 overflow-y-auto">
      <div class="pa-4 pb-2">
        <v-btn
            color="secondary"
            variant="outlined"
            block
            @click="handleNewProjectClick"
        >
          <v-icon :icon="Plus" start size="18" />
          Neues Projekt
        </v-btn>
      </div>

      <v-divider class="my-3" />

      <div class="px-4">
        <h3 class="text-subtitle-1 mb-3 d-flex align-center">
          <v-icon :icon="Clock" size="16" class="me-2" />
          Ihre Projekte
        </h3>
        <v-list density="compact" nav class="pa-0">
          <v-list-item
              v-for="project in recentProjects"
              :key="project.id"
              @click="emit('projectSelect', project)"
              class="mb-2 rounded-lg"
              :title="project.name"
              :subtitle="project.query"
              lines="three"
          >
            <template #prepend>
              <v-icon :icon="FolderOpen" color="blue-darken-2"></v-icon>
            </template>
            <template #append>
                <span class="text-caption text-medium-emphasis me-2">
                    {{ project.date }} • {{ project.outputs.length }} papers
                </span>
            </template>
          </v-list-item>
        </v-list>
      </div>
    </div>

    <div class="border-t-sm pa-4">
      <h3 class="text-subtitle-1 mb-3 d-flex align-center">
        Account
      </h3>
      <div v-if="!isLoggedIn">
        <v-btn block color="primary" @click="loginDialogOpen = true">
          <v-icon :icon="LogIn" start size="18" />
          Login
        </v-btn>
      </div>
      <div v-else>
        <v-card flat class="pa-3 mb-3 bg-green-lighten-5 border-success">
          <div class="d-flex align-center">
            <v-icon :icon="CheckCircle" color="success" class="me-2" size="18"></v-icon>
            <p class="text-success text-body-2">Erfolgreich eingeloggt</p>
          </div>
        </v-card>
        <v-btn block variant="outlined" color="secondary" @click="emit('logout')">
          <v-icon :icon="LogOut" start size="18" />
          Logout
        </v-btn>
      </div>
    </div>

    <v-dialog v-model="loginDialogOpen" max-width="500">
      <v-card>
        <v-card-title class="text-h5">Login in Ihr Konto</v-card-title>
        <v-card-text>
          <p class="mb-4 text-medium-emphasis">Geben Sie Ihre Anmeldedaten ein, um auf Ihre Projekte zuzugreifen.</p>
          <v-form @submit.prevent="handleLoginSubmit">
            <!--<v-text-field
                v-model="email"
                label="Email"
                type="email"
                variant="outlined"
                required
                class="mb-2"
            ></v-text-field>
            <v-text-field
                v-model="password"
                label="Passwort"
                type="password"
                variant="outlined"
                required
                class="mb-4"
            ></v-text-field>-->
            <v-text-field
              v-model="username"
              label="Username"
              type="text"
              variant="outlined"
              required
              class="mb-4"
            ></v-text-field>
            <v-btn type="submit" color="primary" block>Login</v-btn>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="secondary" variant="text" @click="loginDialogOpen = false">Schließen</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<style scoped>
.border-b-sm {
  border-bottom: 1px solid #E0E0E0;
}
.border-t-sm {
  border-top: 1px solid #E0E0E0;
}
.bg-green-lighten-5 {
  background-color: #F1F8E9 !important; /* Vuetify's light green */
}
.border-success {
  border: 1px solid #8BC34A !important; /* Vuetify's success green */
}
</style>