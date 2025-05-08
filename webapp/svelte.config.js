import adapter from '@sveltejs/adapter-auto';

/** @type {import('@sveltejs/kit').Config} */
const config = {
	kit: {
		adapter: adapter(),
		csrf: {
			checkOrigin: true,
		},
		alias: {
			$lib: 'src/lib',
			$components: 'src/components',
			$stores: 'src/stores',
			$utils: 'src/utils'
		}
	}
};

export default config; 