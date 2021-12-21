<script>
    import Loading from "../../components/Loading.svelte"
</script>

{#await fetch("/api/pemesanan").then(r => r.json())}
    <Loading/>
{:then data}
    <ul>
        {#each Object.values(data) as item}
            <li>
                <a href="pemesanan/{item.id}">{item.id}</a>
                <p>{JSON.stringify(item)}</p>
            </li>
        {/each}
    </ul>
{/await}

<style>
    ul {
        padding: 1rem;
    }

    li {
        list-style: none;
    }
</style>