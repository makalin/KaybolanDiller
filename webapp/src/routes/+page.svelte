<script>
  import { onMount } from 'svelte';
  
  let sourceText = '';
  let translatedText = '';
  let sourceLang = 'en';
  let targetLang = 'tr';
  let languages = {
    turkish_dialects: [],
    turkic_languages: [],
    other_languages: []
  };
  let loading = false;
  let error = null;

  onMount(async () => {
    try {
      const response = await fetch('http://localhost:8000/languages');
      languages = await response.json();
    } catch (e) {
      error = 'Failed to load languages';
      console.error(e);
    }
  });

  async function translate() {
    if (!sourceText) return;
    
    loading = true;
    error = null;
    
    try {
      const response = await fetch('http://localhost:8000/translate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: sourceText,
          source_lang: sourceLang,
          target_lang: targetLang
        })
      });
      
      const data = await response.json();
      translatedText = data.translated_text;
    } catch (e) {
      error = 'Translation failed';
      console.error(e);
    } finally {
      loading = false;
    }
  }
</script>

<main class="container">
  <h1>🌍 KaybolanDiller</h1>
  <p class="subtitle">Preserving endangered languages through AI translation</p>

  <div class="translation-container">
    <div class="input-section">
      <select bind:value={sourceLang}>
        <option value="en">English</option>
        {#each Object.entries(languages) as [category, langs]}
          {#each langs as lang}
            <option value={lang.toLowerCase()}>{lang}</option>
          {/each}
        {/each}
      </select>
      
      <textarea
        bind:value={sourceText}
        placeholder="Enter text to translate..."
        rows="5"
      ></textarea>
    </div>

    <div class="output-section">
      <select bind:value={targetLang}>
        <option value="tr">Turkish</option>
        {#each Object.entries(languages) as [category, langs]}
          {#each langs as lang}
            <option value={lang.toLowerCase()}>{lang}</option>
          {/each}
        {/each}
      </select>
      
      <div class="translation-output">
        {#if loading}
          <p>Translating...</p>
        {:else if error}
          <p class="error">{error}</p>
        {:else}
          <p>{translatedText || 'Translation will appear here'}</p>
        {/if}
      </div>
    </div>
  </div>

  <button on:click={translate} disabled={loading || !sourceText}>
    {loading ? 'Translating...' : 'Translate'}
  </button>
</main>

<style>
  .container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
    font-family: system-ui, -apple-system, sans-serif;
  }

  h1 {
    text-align: center;
    color: #2c3e50;
    margin-bottom: 0.5rem;
  }

  .subtitle {
    text-align: center;
    color: #666;
    margin-bottom: 2rem;
  }

  .translation-container {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2rem;
    margin-bottom: 2rem;
  }

  .input-section,
  .output-section {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  select {
    padding: 0.5rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 1rem;
  }

  textarea {
    padding: 1rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 1rem;
    resize: vertical;
  }

  .translation-output {
    min-height: 150px;
    padding: 1rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    background: #f9f9f9;
  }

  button {
    display: block;
    width: 200px;
    margin: 0 auto;
    padding: 1rem;
    background: #3498db;
    color: white;
    border: none;
    border-radius: 4px;
    font-size: 1rem;
    cursor: pointer;
    transition: background 0.3s;
  }

  button:hover {
    background: #2980b9;
  }

  button:disabled {
    background: #bdc3c7;
    cursor: not-allowed;
  }

  .error {
    color: #e74c3c;
  }
</style> 