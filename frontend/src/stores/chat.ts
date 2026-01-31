import { defineStore } from 'pinia';
import { ref } from 'vue';
import { chatWithPaper } from '@/services/papers';
import type { ChatMessageDto } from '@/api/models';

export const useChatStore = defineStore('chat', () => {
    /**
     * Session-scoped cache (cleared on page refresh)
     * Key: paperId, Value: Array of messages
     */
    const chatHistory = ref<Map<number, ChatMessageDto[]>>(new Map());
    const isSending = ref(false);

    /**
     * Returns the chat history for a specific paper.
     */
    function getMessages(paperId: number): ChatMessageDto[] {
        return chatHistory.value.get(paperId) ?? [];
    }

    /**
     * Sends a message to the AI and updates the local session history.
     */
    async function sendMessage(paperId: number, userMessage: string) {
        if (!userMessage.trim()) return;

        // 1. Initialize session for this specific paper if it doesn't exist
        if (!chatHistory.value.has(paperId)) {
            chatHistory.value.set(paperId, []);
        }

        const history = chatHistory.value.get(paperId)!;

        /**
         * 2. Capture current history context BEFORE adding the new message.
         * The backend expects 'message' as the new prompt and 'history' as strictly prior exchanges.
         */
        const historyContext = [...history];

        // 3. Add User Message to local state immediately for UI responsiveness
        const userMsg: ChatMessageDto = { role: 'user', content: userMessage };
        history.push(userMsg);

        isSending.value = true;
        try {
            /**
             * 4. Call Consolidated Backend Service.
             * We pass the new message separately from the historical context.
             */
            const response = await chatWithPaper(paperId, {
                message: userMessage,
                history: historyContext
            });

            // 5. Add AI Response to local state
            history.push({
                role: 'assistant',
                content: response.answer
            });
        } catch (error) {
            console.error('Failed to get AI response:', error);

            history.push({
                role: 'assistant',
                content: 'An error occurred while communicating with the AI. Please try again later.'
            });
        } finally {
            isSending.value = false;
        }
    }

    /**
     * Clears the chat history for a specific paper.
     */
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