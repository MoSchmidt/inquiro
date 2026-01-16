import { defineStore } from 'pinia';
import { ref } from 'vue';
import { chatWithPaper } from '@/services/papers';
import type { ChatMessageDto } from '@/api/models';

export const useChatStore = defineStore('chat', () => {
    // Session-scoped cache (cleared on page refresh)
    // Key: paperId, Value: Array of messages
    const chatHistory = ref<Map<number, ChatMessageDto[]>>(new Map());
    const isSending = ref(false);

    /**
     * Returns the chat history for a specific paper.
     */
    function getMessages(paperId: number): ChatMessageDto[] {
        return chatHistory.value.get(paperId) ?? [];
    }

    /**
     * Sends a message to the AI and updates the session history.
     */
    async function sendMessage(paperId: number, userMessage: string) {
        if (!userMessage.trim()) return;

        // 1. Initialize session if it doesn't exist
        if (!chatHistory.value.has(paperId)) {
            chatHistory.value.set(paperId, []);
        }

        const history = chatHistory.value.get(paperId)!;

        // 2. Add User Message to local state
        const userMsg: ChatMessageDto = { role: 'user', content: userMessage };
        history.push(userMsg);

        isSending.value = true;
        try {
            // 3. Call Backend (History is sent for session context)
            // We slice history to avoid sending the message we just added in the 'message' field
            const response = await chatWithPaper(paperId, {
                message: userMessage,
                history: history.slice(0, -1)
            });

            // 4. Add AI Response to local state
            history.push({
                role: 'assistant',
                content: response.answer
            });
        } catch (error) {
            console.error('Failed to get AI response:', error);
            // Optional: Add an error message to the chat UI
            history.push({
                role: 'assistant',
                content: 'Sorry, I encountered an error processing your request.'
            });
        } finally {
            isSending.value = false;
        }
    }

    function clearSession(paperId: number) {
        chatHistory.value.delete(paperId);
    }

    return {
        getMessages,
        sendMessage,
        isSending,
        clearSession
    };
});