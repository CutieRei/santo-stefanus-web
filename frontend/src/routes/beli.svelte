
<form method="post" action="http://localhost:8000/beli">
    <input name="fullname" placeholder="full name">
    <input name="address" placeholder="address">
    <input name="email" placeholder="email" type="email">
    <input name="phone" placeholder="phone" type="tel">
    <textarea name="description" placeholder="description"></textarea>
    <button type="submit">Confirm</button>
</form>

<style>
    form {
        display: flex;
        flex-direction: column;
        height: 100vh;
    }

    form * {
        height: 10%;
    }
</style>