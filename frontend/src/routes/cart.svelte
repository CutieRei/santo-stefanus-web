
<script lang="ts">

    import Loading from "../components/Loading.svelte"
    import { onMount } from "svelte"

    interface Item {
        id: string
        name: string
        quantity: number
        price: number
        total_price: string
    }
    interface Cart {
        [ key: string]: Item
    }
    let cart: Cart = {};

    async function updateItem(e: MouseEvent) {
        let button = <HTMLButtonElement>e.target
        let id = button.parentElement.getAttribute("data-item-id")
        button.disabled = true
        let uquantity = parseInt(<string>(<unknown>cart[id].quantity))
        let data: {id: string, total: number, name: string} = await fetch(`/api/items/${id}`).then(r => {
            if(r.status == 200) {
                return r.json()
            }
        })
        if(data) {
            let { quantity } = await fetch(`/api/cart?id=${data.id}`).then(r => r.json())
            if(data.total < uquantity) {
                cart[id].quantity = quantity.toString()
                alert(`${data.name} current stock is ${data.total}`)
            } else {
                if(quantity > uquantity) {
                    await fetch(`/api/cart?id=${id}&quantity=${quantity-uquantity}`, {
                        method: "delete"
                    })
                } else {
                    await fetch(`/api/cart?id=${id}&quantity=${quantity-uquantity}`, {
                        method: "post",
                        body: JSON.stringify({
                            id: id,
                            quantity: uquantity - quantity
                        }),
                        headers: {
                            'Accept': 'application/json',
                            'Content-Type': 'application/json'
                        }
                    })
                }
                let item = cart[id]
                cart[id].total_price = (item.price*item.quantity).toLocaleString("en-US")
                button.disabled = false
            }
        }
    }

    async function deleteItem(e: MouseEvent) {
        let form =  (<HTMLButtonElement>e.target).parentElement
        let id = form.getAttribute("data-item-id")
        let val = confirm(`are you sure you want to delete ${cart[id].name}`)
        if(val) {
            await fetch(`/api/cart?id=${id}`, {
                method: "delete"
            })
            if((form.parentElement.children.length - 1) == 0) {
                let h1 = document.createElement("h1")
                h1.innerText = "Empty..."
                form.parentElement.parentElement.parentElement.appendChild(h1)
                form.parentElement.parentElement.remove();
                (<HTMLButtonElement>document.querySelector("#submitter")).disabled = true
            }
            form.parentElement.remove()
        }
    }

    async function init() {
        let data = <Promise<Item[]>>await fetch("/api/cart").then(r => r.json())
        for(let item of Object.values(data)) {
            cart[item.id] = {...item, total_price: (item.price*item.quantity).toLocaleString("en-US")}
        }
        if(Object.keys(data).length != 0) (<HTMLButtonElement>document.querySelector("#submitter")).disabled = false
        return data
    }

</script>

<form action="/api/pay" method="post">
    <div>
        <input required name="fullname" placeholder="fullname">
        <input required name="address" placeholder="address">
        <input required name="email" type="email" placeholder="email">
        <input required name="phone" type="tel" placeholder="phone number">
        <textarea name="description"></textarea>
        <button disabled id="submitter" type="Submit">Confirm</button>
    </div>
</form>
{#await init()}
    <Loading/>
{:then data}
    <div id="item-list">
        {#if Object.keys(data).length == 0}
            <h1>Empty...</h1>
        {:else}
            <ul>
                {#each Object.values(data) as item}
                <li id="item-{item.id}">
                    <form data-item-id={item.id}>
                        <p>{item.name}</p>
                        <p>Quantity</p>
                        <input type="number" bind:value={cart[item.id].quantity}>
                        <button on:click|preventDefault="{updateItem}">Confirm</button>
                        <button on:click|preventDefault="{deleteItem}">Remove</button>
                        <p>Total: Rp.{cart[item.id].total_price}</p>
                    </form>
                </li>
                {/each}
            </ul>
        {/if}
    </div>
{/await}

<style lang="scss">
    form {
        div {
            display: flex;
            flex-direction: column;

            * {
                padding: 0.25rem;
            }
        }
    }

    h1 {
        text-align: center;
    }

    li {
        list-style: none;
    }

    ul {
        padding: 1rem;
    }
</style>