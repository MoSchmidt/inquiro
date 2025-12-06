<script setup lang="ts">
import { ref, watch } from 'vue';
import { signup, login } from '@/services/auth';
import { useAuthStore } from '@/stores/auth';

const props = defineProps<{ open: boolean }>();

const emit = defineEmits<{
	(e: 'close'): void;
	(e: 'create', payload: { name: string; email: string; password: string }): void;
}>();

const localOpen = ref(!!props.open);
watch(() => props.open, (v) => (localOpen.value = !!v));
watch(localOpen, (v) => {
	if (!v) emit('close');
});

const name = ref('');
const email = ref('');
const password = ref('');
const confirmPassword = ref('');
const error = ref('');
const loading = ref(false);
const auth = useAuthStore();

const submit = async () => {
	error.value = '';
	if (password.value !== confirmPassword.value) {
		error.value = 'Passwords do not match';
		return;
	}
	if (password.value.length < 8) {
		error.value = 'Password must be at least 8 characters long';
		return;
	}

	loading.value = true;
	try {
		const username = email.value || name.value;
		// create user (backend currently expects `username`)
		await signup(username);

		// immediately login to receive tokens
		const resp = await login(username, password.value);
		if (resp && resp.access_token) {
			auth.setAuth({
				accessToken: resp.access_token,
				refreshToken: resp.refresh_token,
				user: resp.user,
			});
		}

		// keep backward compatibility: emit create event
		emit('create', { name: name.value, email: email.value, password: password.value });

		// clear form and close
		name.value = '';
		email.value = '';
		password.value = '';
		confirmPassword.value = '';
		localOpen.value = false;
	} catch (err: unknown) {
		try {
			// axios-style error handling
			// @ts-ignore
			error.value = err?.response?.data?.detail || err?.message || 'Signup failed';
		} catch {
			error.value = 'Signup failed';
		}
	} finally {
		loading.value = false;
	}
};
</script>

<template>
	<v-dialog v-model="localOpen" max-width="560">
		<v-card>
			<v-card-title>Create Account</v-card-title>

			<v-card-text>
				<div class="space-y-4">
					<v-text-field v-model="name" label="Full name" required />
					<v-text-field v-model="email" label="Email address" type="email" required />
					<v-text-field v-model="password" label="Password" type="password" required />
					<v-text-field v-model="confirmPassword" label="Confirm password" type="password" required />

					<div v-if="error" class="mt-2" style="color:var(--v-theme-error)">{{ error }}</div>
				</div>
			</v-card-text>

			<v-card-actions>
				<v-spacer />
				<v-btn text @click="localOpen = false">Cancel</v-btn>
				<v-btn color="primary" @click="submit">Create Account</v-btn>
			</v-card-actions>
		</v-card>
	</v-dialog>
</template>

<style scoped></style>
