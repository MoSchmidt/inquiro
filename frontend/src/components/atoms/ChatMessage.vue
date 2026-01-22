<script setup lang="ts">
import { computed } from 'vue';
import { VAvatar, VIcon } from 'vuetify/components';
import { User, Sparkles } from 'lucide-vue-next';
import FormattedMarkdown from './FormattedMarkdown.vue';
import type { ChatMessageDto } from '@/api/models';

const props = defineProps<{
  message: ChatMessageDto;
}>();

const isUser = computed(() => props.message.role === 'user');
</script>

<template>
  <div
    class="chat-message d-flex ga-3"
    :class="{ 'user-message': isUser, 'assistant-message': !isUser }"
  >
    <v-avatar
      :color="isUser ? 'primary' : 'secondary'"
      size="32"
      class="flex-shrink-0"
    >
      <v-icon :icon="isUser ? User : Sparkles" size="18" />
    </v-avatar>

    <div class="message-content flex-grow-1">
      <div class="message-role text-caption font-weight-medium mb-1">
        {{ isUser ? 'You' : 'AI Assistant' }}
      </div>
      <div class="message-body pa-3 rounded-lg">
        <template v-if="isUser">
          <p class="text-body-2 mb-0" style="white-space: pre-wrap;">{{ message.content }}</p>
        </template>
        <template v-else>
          <FormattedMarkdown :markdown="message.content" />
        </template>
      </div>
    </div>
  </div>
</template>

<style scoped>
.chat-message {
  padding: 8px 0;
}

.user-message .message-body {
  background-color: rgb(var(--v-theme-primary), 0.08);
  border: 1px solid rgb(var(--v-theme-primary), 0.15);
}

.assistant-message .message-body {
  background-color: rgb(var(--v-theme-surface-variant));
  border: 1px solid rgb(var(--v-theme-outline-variant), 0.3);
}

.message-role {
  color: rgb(var(--v-theme-on-surface-variant));
}
</style>
