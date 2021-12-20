<nav>
    <div id="nav-url">
        <a href="/">Home</a>
        <a href="/cart">Checkout</a>
    </div>
</nav>

<style lang="scss">
    nav {
        display: flex;
        flex-direction: row-reverse;
        max-height: max-content;
        width: 100%;
        font-size: 1rem;
        background-color: #e2e2e2;

        #nav-url {
            padding: 1rem;

            a {
                margin: 0 1rem 0 1rem;
                text-decoration: none;
                color: black;
                transition: all 150ms;
                text-align: center;
            }

            a:hover {
                text-shadow: 0 0 5px black;
            }
        }
    }

    @media screen and (max-width: 728px) {
        nav {
            flex-direction: row;
            justify-content: center;
            align-items: center;
        }
    }
</style>