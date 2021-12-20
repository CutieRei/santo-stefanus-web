<script>
    import Nav from "../components/Nav.svelte"
</script>

<main>
    <Nav/>
    <div id="actual-body">
        <div>
            <slot></slot>
        </div>
    </div>
</main>

<style lang="scss">
    main {
        display: flex;
        flex-direction: column;
        align-items: center;
        width: 100vw;
        height: 100vh;
        background-color: rgba(0,0,0,0);

        #actual-body {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100%;

            div {
                background-color: white;
                border-radius: 10px;
                padding: 1rem;
            }
        }
    }
</style>