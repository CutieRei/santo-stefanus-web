
<ul>
    {#await fetch("/api/items").then(r => r.json())}
        <p>fetching...</p>
    {:then items}
        {#each items as item}
            <li>
                <a href="/barang/{item.id}">{item.name}</a>
                <p>Rp.{item.price.toLocaleString("en-US")}</p>
            </li>
        {/each}
    {/await}
</ul>

<style>

    ul {
        padding: 1rem;
    }
    li {
        list-style: none;
        margin: 0;
    }
</style>