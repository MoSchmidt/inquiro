<script setup lang="ts">
import { ref } from 'vue';
import { VCard, VCardTitle, VCardText, VTextarea, VBtn, VIcon, VRow, VCol } from 'vuetify/components';
import { Send } from 'lucide-vue-next';

const emit = defineEmits(['submit']);

const input = ref('');

const handleSubmit = () => {
  if (input.value.trim()) {
    emit('submit', input.value);
    input.value = '';
  }
};
</script>

<template>
  <div class="input-wrapper">
    <v-container fluid class="fill-height align-center justify-center">
      <div class="w-100" style="max-width: 900px;">
        <div class="text-center mb-10">
          <h2 class="text-h4 mb-2">Willkommen beim AI Text Processor</h2>
          <p class="text-medium-emphasis">
            Geben Sie Ihre Texteingabe unten ein und lassen Sie unsere KI leistungsstarke Ergebnisse für Sie generieren
          </p>
        </div>

        <v-form @submit.prevent="handleSubmit">
          <v-textarea
              v-model="input"
              label="Geben Sie Ihren Text hier ein..."
              variant="outlined"
              auto-grow
              rows="8"
              class="mb-4"
          ></v-textarea>
          <v-btn
              type="submit"
              color="primary"
              block
              size="large"
              :disabled="!input.trim()"
          >
            <v-icon :icon="Send" start></v-icon>
            Ergebnis generieren
          </v-btn>
        </v-form>

        <v-row class="mt-12">
          <v-col cols="12" md="4">
            <v-card flat class="pa-4 text-center border-sm">
              <div class="d-flex align-center justify-center mx-auto mb-4 bg-blue-lighten-4 rounded-circle" style="width: 48px; height: 48px;">
                <span class="text-blue-darken-2 text-h6">1</span>
              </div>
              <v-card-title class="text-h6 mb-2 pa-0">Eingabe</v-card-title>
              <v-card-text class="text-medium-emphasis pa-0 text-body-2">
                Geben Sie Ihre Textabfrage oder Anfrage ein
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12" md="4">
            <v-card flat class="pa-4 text-center border-sm">
              <div class="d-flex align-center justify-center mx-auto mb-4 bg-blue-lighten-4 rounded-circle" style="width: 48px; height: 48px;">
                <span class="text-blue-darken-2 text-h6">2</span>
              </div>
              <v-card-title class="text-h6 mb-2 pa-0">KI-Verarbeitung</v-card-title>
              <v-card-text class="text-medium-emphasis pa-0 text-body-2">
                Unsere KI wertet Ihre Eingabe aus und verarbeitet sie
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12" md="4">
            <v-card flat class="pa-4 text-center border-sm">
              <div class="d-flex align-center justify-center mx-auto mb-4 bg-blue-lighten-4 rounded-circle" style="width: 48px; height: 48px;">
                <span class="text-blue-darken-2 text-h6">3</span>
              </div>
              <v-card-title class="text-h6 mb-2 pa-0">Ergebnisse</v-card-title>
              <v-card-text class="text-medium-emphasis pa-0 text-body-2">
                Erhalten Sie organisierte Ergebnisordner
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </div>
    </v-container>
  </div>

</template>

<style scoped>
/* Vuetify-Klassen werden bevorzugt, aber einige benutzerdefinierte Stile für die Kreise */
.bg-blue-lighten-4 {
  background-color: #E3F2FD !important; /* Vuetify's light blue */
}
.text-blue-darken-2 {
  color: #1976D2 !important; /* Vuetify's darker blue */
}
.border-sm {
  border: 1px solid #E0E0E0; /* Light border similar to tailwind's gray-200 */
}
.input-wrapper {
  max-height: 85vh;
  overflow-y: auto;
  padding-right: 6px;
}

</style>