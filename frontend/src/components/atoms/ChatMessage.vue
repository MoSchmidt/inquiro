<script setup lang="ts">
import { computed } from 'vue';
import { VAvatar, VIcon } from 'vuetify/components';
import { User, Sparkles } from 'lucide-vue-next';
import type { ChatMessageDto } from '@/api/models';
import ChatMarkdown from '@/components/atoms/ChatMarkdown.vue';

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
      :color="isUser ? '#1976D2' : '#FF6B35'"
      size="32"
      class="flex-shrink-0"
    >
      <v-icon :icon="isUser ? User : Sparkles" size="18" color="white" />
    </v-avatar>

    <div class="message-content flex-grow-1" style="min-width: 0;">
      <div class="message-role text-caption font-weight-medium mb-1">
        {{ isUser ? 'You' : 'AI Assistant' }}
      </div>

      <div class="message-body pa-3 rounded-lg">
        <template v-if="isUser">
          <div class="text-body-2 mb-0" style="white-space: pre-wrap;">{{ message.content }}</div>
        </template>

        <template v-else>
          <ChatMarkdown :content="message.content" />
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
  background-color: rgb(var(--v-theme-surface));
  border: 1px solid rgb(var(--v-theme-outline-variant), 0.2);
}

.message-role {
  color: rgb(var(--v-theme-on-surface));
  opacity: 0.8;
}
</style>