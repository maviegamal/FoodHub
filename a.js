function Cart({
  cart,
    removeFromCart,
    increase,
    decrease,
    subtotal,
    deliveryFee,
    total,
    checkout
}) {

    if (cart.length === 0) {

        return (
            <section className="container text-center py-5">

                <div className="display-1">
                    🛒
                </div>

                <h2 className="mt-3">
                    Your cart is empty
                </h2>

                <p className="text-muted">
                    Add some delicious food first!
                </p>

            </section>
        );

    }

    return (

        <section className="container py-5">

            <h1 className="section-title mb-5">
                Your Cart 🛒
            </h1>

            <div className="row">

                <div className="col-lg-8">

                    {cart.map(item => (

                        <div
                            className="card mb-3 shadow-sm"
                            key={item.id}
                        >

                            <div className="card-body">

                                <div className="row align-items-center">

                                    <div className="col-3">

                                        <img
                                            src={item.image}
                                            className="cart-image"
                                            alt={item.name}
                                        />

                                    </div>

                                    <div className="col-5">

                                        <h5>{item.name}</h5>

                                        <p className="text-muted">
                                            ${item.price}
                                        </p>

                                    </div>

                                    <div className="col-4">

                                        <div className="d-flex align-items-center">

                                            <button
                                                className="btn btn-outline-dark btn-sm"
                                                onClick={() => decrease(item.id)}
                                            >
                                                -
                                            </button>

                                            <span className="mx-3">
                                                {item.quantity}
                                            </span>

                                            <button
                                                className="btn btn-outline-dark btn-sm"
                                                onClick={() => increase(item.id)}
                                            >
                                                +
                                            </button>

                                            <button
                                                className="btn btn-danger btn-sm ms-3"
                                                onClick={() => removeFromCart(item.id)}
                                            >
                                                ×
                                            </button>

                                        </div>

                                    </div>

                                </div>

                            </div>

                        </div>

                    ))}

                </div>

                <div className="col-lg-4">

                    <div className="card shadow">

                        <div className="card-body">

                            <h4 className="mb-4">
                                Order Summary
                            </h4>

                            <div className="d-flex justify-content-between mb-2">
                                <span>Subtotal</span>
                                <span>${subtotal.toFixed(2)}</span>
                            </div>

                            <div className="d-flex justify-content-between mb-2">
                                <span>Delivery Fee</span>
                                <span>${deliveryFee.toFixed(2)}</span>
                            </div>

                            <hr />

                            <div className="d-flex justify-content-between fw-bold fs-5">
                                <span>Total</span>
                                <span>${total.toFixed(2)}</span>
                            </div>

                            <button
                                className="btn btn-warning w-100 mt-4"
                                onClick={checkout}
                            >
                                Proceed to Checkout
                            </button>

                        </div>

                    </div>

                </div>

            </div>

        </section>

    );

}



/* =========================
   Footer
========================= */

function Footer() {

    return (

        <footer>

            <div className="container">

                <div className="row">

                    <div className="col-md-4">

                        <h3>
                            🍔 FoodHub
                        </h3>

                        <p className="text-secondary">
                            Delicious food made with love.
                        </p>

                    </div>


                    <div className="col-md-4">

                        <h5>
                            Opening Hours
                        </h5>

                        <p className="text-secondary">
                            Monday - Friday: 10 AM - 11 PM
                        </p>

                    </div>


                    <div className="col-md-4">

                        <h5>
                            Contact
                        </h5>

                        <p className="text-secondary">
                            📍 Cairo, Egypt
                        </p>

                        <p className="text-secondary">
                            📞 +20 123 456 789
                        </p>

                    </div>

                </div>

                <hr />

                <p className="text-center text-secondary mb-0">
                    © 2026 FoodHub. All Rights Reserved.
                </p>

            </div>

        </footer>

    );
}


/* =========================
   Main App
========================= */

function App() {

    const [page, setPage] = useState("home");


    const [foods, setFoods] = useState([]);

    const [loading, setLoading] = useState(true);

    const [error, setError] = useState("");


    const [cart, setCart] = useState([]);


    /* Fake API */

    useEffect(() => {

        const fetchFoods = async () => {

            try {

                const response = await fetch(
                    "https://dummyjson.com/recipes?limit=30"
                );


                if (!response.ok) {

                    throw new Error(
                        "Failed to fetch data"
                    );

                }


                const data =
                    await response.json();


                const formattedFoods =
                    data.recipes.map(food => ({

                        id: food.id,

                        name: food.name,

                        image: food.image,

                        cuisine: food.cuisine,

                        rating: food.rating,

                        description:
                            food.instructions
                                ?.slice(0, 100) ||
                            "Delicious meal prepared with fresh ingredients.",

                        price:
                            Math.floor(
                                Math.random() * 15
                            ) + 8

                    }));


                setFoods(formattedFoods);

            }

            catch (error) {

                setError(
                    "Could not load the menu."
                );

            }

            finally {

                setLoading(false);

            }

        };


        fetchFoods();

    }, []);


    /* Add To Cart */

    const addToCart = (food) => {

        setCart(oldCart => {

            const existing =
                oldCart.find(
                    item => item.id === food.id
                );


            if (existing) {

                return oldCart.map(item =>

                    item.id === food.id

                        ? {
                            ...item,
                            quantity:
                                item.quantity + 1
                        }

                        : item

                );

            }


            return [

                ...oldCart,

                {
                    ...food,
                    quantity: 1
                }

            ];

        });

    };


    /* Remove */

    const removeFromCart = (id) => {

        setCart(
            oldCart =>
                oldCart.filter(
                    item => item.id !== id
                )
        );

    };


    /* Increase */

    const increase = (id) => {

        setCart(oldCart =>

            oldCart.map(item =>

                item.id === id

                    ? {
                        ...item,
                        quantity:
                            item.quantity + 1
                    }

                    : item

            )

        );

    };


    /* Decrease */

    const decrease = (id) => {

        setCart(oldCart =>

            oldCart

                .map(item =>

                    item.id === id

                        ? {
                            ...item,
                            quantity:
                                item.quantity - 1
                        }

                        : item

                )

                .filter(
                    item => item.quantity > 0
                )

        );

    };


    /*new chechout function*/
    
const subtotal = cart.reduce(
    (total, item) => total + item.price * item.quantity,
    0
);

const deliveryFee = cart.length > 0 ? 5 : 0;

const total = subtotal + deliveryFee;

const checkout = () => {

    if (cart.length === 0) {

        alert("Your cart is empty!");
        return;

    }

    alert(
        "Order placed successfully! Total: $" + total.toFixed(2)
    );

    setCart([]);
    setPage("home");

};

   






    return (

        <>

            <Navbar
                cartCount={cart.length}
                setPage={setPage}
            />


            {page === "home" && (

                <Home
                    setPage={setPage}
                />

            )}


            {page === "menu" && (

                <Menu
                    foods={foods}
                    loading={loading}
                    error={error}
                    addToCart={addToCart}
                />

            )}


            {page === "about" && (

                <About />

            )}


            {page === "contact" && (

                <Contact />

            )}


            {page === "cart" && (

    <Cart
        cart={cart}
        removeFromCart={removeFromCart}
        increase={increase}
        decrease={decrease}
        subtotal={subtotal}
        deliveryFee={deliveryFee}
        total={total}
        checkout={checkout}
    />

)}


            <Footer />

        </>

    );

}


/* =========================
   Render
========================= */

const root =
    ReactDOM.createRoot(
        document.getElementById("root")
    );


root.render(
    <App />
);

