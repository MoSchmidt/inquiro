<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue';
import { VBtn, VIcon, VTextarea, VProgressCircular, VDivider } from 'vuetify/components';
import { Send, Trash2, MessageSquare, X, GripVertical } from 'lucide-vue-next';
import { useChatStore } from '@/stores/chat';
import ChatMessage from '@/components/atoms/ChatMessage.vue';

const props = defineProps<{
  paperId: number;
  paperTitle?: string;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
}>();

const chatStore = useChatStore();
const userInput = ref('');
const messagesContainer = ref<HTMLElement | null>(null);

// Panel width for resizing
const panelWidth = ref(400);
const isResizing = ref(false);
const minWidth = 300;
const maxWidth = 700;

const messages = computed(() => chatStore.getMessages(props.paperId));
const isSending = computed(() => chatStore.isSending);

const hasMessages = computed(() => messages.value.length > 0);

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
    }
  });
};

const sendMessage = async () => {
  const message = userInput.value.trim();
  if (!message || isSending.value) return;

  userInput.value = '';
  scrollToBottom();

  await chatStore.sendMessage(props.paperId, message);
  scrollToBottom();
};

const clearChat = () => {
  chatStore.clearSession(props.paperId);
};

const handleKeydown = (event: KeyboardEvent) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    sendMessage();
  }
};

// Resize handling
const startResize = (event: MouseEvent) => {
  isResizing.value = true;
  const startX = event.clientX;
  const startWidth = panelWidth.value;

  const onMouseMove = (e: MouseEvent) => {
    const delta = startX - e.clientX;
    const newWidth = Math.min(maxWidth, Math.max(minWidth, startWidth + delta));
    panelWidth.value = newWidth;
  };

  const onMouseUp = () => {
    isResizing.value = false;
    document.removeEventListener('mousemove', onMouseMove);
    document.removeEventListener('mouseup', onMouseUp);
  };

  document.addEventListener('mousemove', onMouseMove);
  document.addEventListener('mouseup', onMouseUp);
};

// Auto-scroll when new messages arrive
watch(messages, () => {
  scrollToBottom();
}, { deep: true });
</script>

<template>
  <div
    class="chat-panel d-flex flex-column"
    :style="{ width: `${panelWidth}px` }"
  >
    <!-- Resize Handle -->
    <div
      class="resize-handle d-flex align-center justify-center"
      @mousedown="startResize"
    >
      <v-icon :icon="GripVertical" size="16" class="text-medium-emphasis" />
    </div>

    <!-- Main Panel Content -->
    <div class="chat-panel-inner d-flex flex-column flex-grow-1">
      <!-- Header -->
      <div class="chat-header d-flex align-center px-4 py-3 border-b">
        <v-icon :icon="MessageSquare" size="20" class="text-primary me-2" />
        <span class="text-subtitle-2 font-weight-medium flex-grow-1">Chat with Paper</span>

        <v-btn
          v-if="hasMessages"
          icon
          title="Clear chat"
          variant="text"
          size="x-small"
          @click="clearChat"
        >
          <v-icon :icon="Trash2" size="16" />
        </v-btn>

        <v-btn
          icon
          class="ms-1"
          variant="text"
          size="x-small"
          @click="emit('close')"
        >
          <v-icon :icon="X" size="18" />
        </v-btn>
      </div>

      <!-- Messages Area -->
      <div
        ref="messagesContainer"
        class="messages-container flex-grow-1 overflow-y-auto px-4 py-3"
      >
        <!-- Empty State -->
        <div
          v-if="!hasMessages"
          class="empty-state d-flex flex-column align-center justify-center h-100 text-center"
        >
          <v-icon :icon="MessageSquare" size="48" class="text-medium-emphasis mb-3" />
          <p class="text-body-2 text-medium-emphasis mb-2">
            Ask questions about this paper
          </p>
          <p class="text-caption text-disabled" style="max-width: 250px;">
            The AI will answer based on the paper's content, citing relevant sections.
          </p>
        </div>

        <!-- Messages List -->
        <template v-else>
          <ChatMessage
            v-for="(message, index) in messages"
            :key="index"
            :message="message"
          />

          <!-- Typing Indicator -->
          <div v-if="isSending" class="typing-indicator d-flex align-center ga-2 py-2">
            <v-progress-circular
              indeterminate
              size="16"
              width="2"
              color="primary"
            />
            <span class="text-caption text-medium-emphasis">AI is thinking...</span>
          </div>
        </template>
      </div>

      <v-divider />

      <!-- Input Area -->
      <div class="chat-input-area pa-3">
        <div class="d-flex align-end ga-2">
          <v-textarea
            v-model="userInput"
            :disabled="isSending"
            placeholder="Ask a question about this paper..."
            variant="outlined"
            density="compact"
            rows="1"
            max-rows="4"
            auto-grow
            hide-details
            class="flex-grow-1"
            @keydown="handleKeydown"
          />
          <v-btn
            icon
            color="primary"
            size="small"
            :loading="isSending"
            :disabled="!userInput.trim() || isSending"
            @click="sendMessage"
          >
            <v-icon :icon="Send" size="18" />
          </v-btn>
        </div>
        <p class="text-caption text-disabled mt-2">
          Press Enter to send, Shift+Enter for new line
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.chat-panel {
  height: 100%;
  background-color: rgb(var(--v-theme-surface));
  border-left: 1px solid rgb(var(--v-theme-outline-variant));
  display: flex;
  flex-direction: row;
  position: relative;
}

.resize-handle {
  width: 8px;
  cursor: ew-resize;
  background-color: rgb(var(--v-theme-surface-variant));
  border-right: 1px solid rgb(var(--v-theme-outline-variant));
  transition: background-color 0.2s ease;
  flex-shrink: 0;
}

.resize-handle:hover {
  background-color: rgb(var(--v-theme-primary), 0.1);
}

.chat-panel-inner {
  flex-grow: 1;
  min-width: 0;
  overflow: hidden;
}

.chat-header {
  background-color: rgb(var(--v-theme-surface));
  flex-shrink: 0;
}

.messages-container {
  background-color: rgb(var(--v-theme-background));
}

.empty-state {
  min-height: 200px;
}

.chat-input-area {
  background-color: rgb(var(--v-theme-surface));
  flex-shrink: 0;
}

.typing-indicator {
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
</style>
