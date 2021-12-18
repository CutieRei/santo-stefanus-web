
<script context="module">

    export async function load({ fetch, page}) {
        let data = await fetch(`http://${page.host}/api/items/${page.params.id}`).then(r => {
            if(r.status == 200) return r.json()
        })
        if(data == null) return {
            redirect: "/404",
            status: 301
        }
        return { props: {
            item: data
        }}
    }

</script>

<script lang="ts">
    import Loading from "../../components/Loading.svelte"
    export let item: {id: string, name: string, price: number, total: number}
    let value: string;

    function quantityChange() {
        let button = <HTMLButtonElement>document.querySelector("#add-cart")
        let value = parseInt(value)
        if(isNaN(value) || value > item.total) button.disabled = true
        else button.disabled = false;
    }

    async function init() {
        let r = await fetch(`/api/cart?id=${item.id}`)
        if(r.status == 200) {
            let data = await r.json()
            value = data.quantity
        }
    }

    async function submit() {
        let input = <HTMLInputElement>document.querySelector("#quantity")
        await fetch("/api/cart", {
            method: "post",
            body: JSON.stringify({
                id: item.id,
                quantity: in
            }),
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        })
    }
</script>

<h1>{item.name}</h1>
<p>Rp.{item.price?.toLocaleString("en-US")}</p>
<p>{item.total} tersisa</p>
<form>
    {#await init()}
        <Loading/>
    {:then}
        <input bind:value="{value}" on:input="{quantityChange}" id="quantity" name="quantity" type="number" value="{value}">
    {/await}
    <button on:click="{(e) => {e.preventDefault(); document.getElementById('popup').style.display = 'block'}}" id="add-cart" disabled>Add to cart</button>
</form>

<div id="popup">
    <div>
        <div>
            <h1 style="width: 100%; height: 100%; text-align: center">Are you sure?</h1>
            <div>
                <button on:click="{() => document.querySelector('form').submit()}">Yes</button>
                <button on:click="{() => document.getElementById('popup').style.display = 'none'}">No</button>
            </div>
        </div>
    </div>
</div>

<style lang="scss">
    #popup {
        display: none;
        position: fixed;
        top: 0;
        left: 0;
        
        div {
            display: flex;
            width: 100vw;
            height: 100vh;
            background-color: rgba(0,0,0,0.5);
            justify-content: center;
            align-items: center;

            div {
                display: flex;
                justify-content: center;
                align-items: center;
                flex-direction: column;
                background-color: white;
                padding: 1rem;
                width: max-content;
                height: max-content;
                border-radius: 10px;

                div {
                    display: flex;
                    flex-direction: row;
                    padding: 0;
                    width: 100%;
                    height: 100%;
                    button {
                        width: 50%;
                    }
                }
            }
        }
    }
</style>