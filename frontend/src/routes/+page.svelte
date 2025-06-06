<script lang="ts">
	import { goto } from '$app/navigation';
</script>

<div class="min-h-screen flex flex-col items-center justify-center p-8 space-y-6">
	<h1 class="text-4xl font-bold">Scraper Dashboard</h1>

	<p class="text-lg text-gray-600">
		View, manage, and run your scraping sessions from here.
	</p>

	<button
		class="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-lg shadow"
		on:click={() => goto('/sessions')}
	>
		View Sessions
	</button>
</div>