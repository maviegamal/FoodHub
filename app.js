
const { useState, useEffect } = React;


/* =========================
   Navbar
========================= */

/* =========================
   Navbar
========================= */

function Navbar({ setPage, cartCount }) {

    return (

        <nav className="navbar navbar-expand-lg navbar-dark sticky-top">

            <div className="container">

                <button
                    className="navbar-brand btn btn-link text-decoration-none"
                    onClick={() => setPage("home")}
                >
                    🍔 FoodHub
                </button>

                <button
                    className="navbar-toggler"
                    type="button"
                    data-bs-toggle="collapse"
                    data-bs-target="#navbarNav"
                >
                    <span className="navbar-toggler-icon"></span>
                </button>

                <div className="collapse navbar-collapse" id="navbarNav">

                    <ul className="navbar-nav ms-auto">

                        <li className="nav-item">
                            <button
                                className="nav-link btn"
                                onClick={() => setPage("home")}
                            >
                                Home
                            </button>
                        </li>

                        <li className="nav-item">
                            <button
                                className="nav-link btn"
                                onClick={() => setPage("menu")}
                            >
                                Menu
                            </button>
                        </li>

                        <li className="nav-item">
                            <button
                                className="nav-link btn"
                                onClick={() => setPage("cart")}
                            >
                                Cart 🛒 ({cartCount})
                            </button>
                        </li>

                    </ul>

                </div>

            </div>

        </nav>

    );

}

/* =========================
   Food Card - Phase 2
========================= */

function FoodCard({ food, addToCart }) {

    return (

        <div className="col-lg-4 col-md-6 mb-4">

            <div className="card food-card shadow-sm">

                <img
                    src={food.image}
                    className="food-image"
                    alt={food.name}
                />

                <div className="card-body">

                    <h5 className="card-title fw-bold">
                        {food.name}
                    </h5>

                    <p className="text-muted">
                        {food.cuisine}
                    </p>

                    <p>
                        {food.description}
                    </p>

                    <div className="d-flex justify-content-between align-items-center">

                        <span className="fw-bold text-warning fs-5">
                            ${food.price}
                        </span>

                        <span>
                            ⭐ {food.rating}
                        </span>

                    </div>

                    <button
                        className="btn btn-warning w-100 mt-3"
                        onClick={() => addToCart(food)}
                    >
                        Add To Cart 🛒
                    </button>

                </div>

            </div>

        </div>

    );

}


/* =========================
   Home - Phase 1
========================= */

function Home({ setPage }) {

    return (

        <>

            <section className="hero">

                <div className="container">

                    <div className="hero-content">

                        <p className="text-warning fw-bold">
                            WELCOME TO FOODHUB
                        </p>

                        <h1 className="hero-title">
                            Delicious Food
                            <br />
                            Made With Love ❤️
                        </h1>

                        <p className="hero-text my-4">
                            Discover delicious meals made with
                            fresh ingredients and amazing flavors.
                        </p>

                        <button
                            className="btn btn-warning btn-lg px-4"
                            onClick={() => setPage("menu")}
                        >
                            Explore Menu
                        </button>

                    </div>

                </div>

            </section>


            <section className="container py-5">

                <div className="text-center mb-5">

                    <h2 className="section-title">
                        Why Choose Us?
                    </h2>

                    <p className="text-muted">
                        Everything you need for a perfect meal.
                    </p>

                </div>


                <div className="row g-4">

                    <div className="col-md-4">
                        <div className="feature-card">

                            <div className="feature-icon">🥗</div>

                            <h4>Fresh Ingredients</h4>

                            <p className="text-muted">
                                We use fresh and high-quality ingredients.
                            </p>

                        </div>
                    </div>


                    <div className="col-md-4">
                        <div className="feature-card">

                            <div className="feature-icon">👨‍🍳</div>

                            <h4>Expert Chefs</h4>

                            <p className="text-muted">
                                Delicious meals prepared by professional chefs.
                            </p>

                        </div>
                    </div>


                    <div className="col-md-4">
                        <div className="feature-card">

                            <div className="feature-icon">🚀</div>

                            <h4>Fast Delivery</h4>

                            <p className="text-muted">
                                Your favorite meals delivered quickly.
                            </p>

                        </div>
                    </div>

                </div>

            </section>

        </>

    );

}


/* =========================
   Menu - Phase 2
========================= */

function Menu({ foods, loading, error, addToCart }) {

    const [search, setSearch] = useState("");

    const [category, setCategory] = useState("All");


    const categories = [
        "All",
        ...new Set(foods.map(food => food.cuisine))
    ];


    const filteredFoods = foods.filter(food => {

        const searchMatch = food.name
            .toLowerCase()
            .includes(search.toLowerCase());

        const categoryMatch =
            category === "All" || food.cuisine === category;

        return searchMatch && categoryMatch;

    });


    return (

        <section className="container py-5">

            <div className="text-center mb-5">

                <h1 className="section-title">
                    Our Menu 🍔
                </h1>

                <p className="text-muted">
                    Choose your favorite meal.
                </p>

            </div>


            <div className="row mb-4">

                <div className="col-md-7 mb-3">

                    <input
                        type="text"
                        className="form-control form-control-lg"
                        placeholder="Search food..."
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                    />

                </div>


                <div className="col-md-5 mb-3">

                    <select
                        className="form-select form-select-lg"
                        value={category}
                        onChange={(e) => setCategory(e.target.value)}
                    >

                        {categories.map(item => (

                            <option key={item} value={item}>
                                {item}
                            </option>

                        ))}

                    </select>

                </div>

            </div>


            {loading && (

                <div className="loading">

                    <div
                        className="spinner-border text-warning"
                        role="status"
                    >
                    </div>

                </div>

            )}


            {error && (

                <div className="alert alert-danger">
                    {error}
                </div>

            )}


            {!loading && !error && (

                <div className="row">

                    {filteredFoods.map(food => (

                        <FoodCard
                            key={food.id}
                            food={food}
                            addToCart={addToCart}
                        />

                    ))}

                    {filteredFoods.length === 0 && (
                        <p className="text-center text-muted">
                            No meals found.
                        </p>
                    )}

                </div>

            )}

        </section>

    );

}
/* =========================
   Cart - Phase 3
========================= */

function Cart({ cart, increaseQuantity, decreaseQuantity, removeFromCart }) {

    return (

        <section className="container py-5">

            <div className="text-center mb-5">

                <h1 className="section-title">
                    Your Shopping Cart 🛒
                </h1>

                <p className="text-muted">
                    Review your selected meals.
                </p>

            </div>

            {cart.length === 0 ? (

                <div className="text-center py-5">

                    <h4>Your cart is empty!</h4>

                    <p className="text-muted">
                        Add some delicious meals from our menu.
                    </p>

                </div>

            ) : (

                <div className="row">

                    {cart.map(item => (

                        <div className="col-12 mb-3" key={item.id}>

                            <div className="card shadow-sm">

                                <div className="card-body">

                                    <div className="row align-items-center">

                                        <div className="col-md-3">

                                            <img
                                                src={item.image}
                                                alt={item.name}
                                                className="img-fluid rounded"
                                            />

                                        </div>

                                        <div className="col-md-3">

                                            <h5>{item.name}</h5>

                                            <p className="text-muted">
                                                ${item.price} each
                                            </p>

                                        </div>

                                        <div className="col-md-3">

                                            <button
                                                className="btn btn-outline-secondary"
                                                onClick={() => decreaseQuantity(item.id)}
                                            >
                                                -
                                            </button>

                                            <span className="mx-3">
                                                {item.quantity}
                                            </span>

                                            <button
                                                className="btn btn-outline-secondary"
                                                onClick={() => increaseQuantity(item.id)}
                                            >
                                                +
                                            </button>

                                        </div>

                                        <div className="col-md-3">

                                            <p className="fw-bold">
                                                ${(item.price * item.quantity).toFixed(2)}
                                            </p>

                                            <button
                                                className="btn btn-danger btn-sm"
                                                onClick={() => removeFromCart(item.id)}
                                            >
                                                Remove
                                            </button>

                                        </div>

                                    </div>

                                </div>

                            </div>

                        </div>

                    ))}

                </div>

            )}

        </section>

    );

}


/* =========================
   Main App
========================= */

function App() {

    const [page, setPage] = useState("home");

    const [foods, setFoods] = useState([]);

    const [cart, setCart] = useState([]);

    const [loading, setLoading] = useState(true);

    const [error, setError] = useState("");


    /* Fetch Food Data from API */

    useEffect(() => {

        const fetchFoods = async () => {

            try {

                const response = await fetch(
                    "https://dummyjson.com/recipes?limit=30"
                );

                if (!response.ok) {
                    throw new Error("Failed to fetch data");
                }

                const data = await response.json();

                const formattedFoods = data.recipes.map(food => ({

                    id: food.id,

                    name: food.name,

                    image: food.image,

                    cuisine: food.cuisine,

                    rating: food.rating,

                    description:
                        food.instructions?.slice(0, 100) ||
                        "Delicious meal prepared with fresh ingredients.",

                    price: Math.floor(Math.random() * 15) + 8

                }));

                setFoods(formattedFoods);

            }

            catch (error) {

                setError("Could not load the menu. Please try again.");

            }

            finally {

                setLoading(false);

            }

        };

        fetchFoods();

    }, []);


    /* Temporary Add To Cart Function */

    /* Add To Cart Function */

const addToCart = (food) => {

    setCart(previousCart => {

        const existingItem = previousCart.find(
            item => item.id === food.id
        );

        if (existingItem) {

            return previousCart.map(item =>
                item.id === food.id
                    ? { ...item, quantity: item.quantity + 1 }
                    : item
            );

        }

        return [...previousCart, { ...food, quantity: 1 }];

    });

};

/* Increase Item Quantity */

const increaseQuantity = (id) => {

    setCart(previousCart =>
        previousCart.map(item =>
            item.id === id
                ? { ...item, quantity: item.quantity + 1 }
                : item
        )
    );

};


/* Decrease Item Quantity */

const decreaseQuantity = (id) => {

    setCart(previousCart =>
        previousCart
            .map(item =>
                item.id === id
                    ? { ...item, quantity: item.quantity - 1 }
                    : item
            )
            .filter(item => item.quantity > 0)
    );

};


/* Remove Item From Cart */

const removeFromCart = (id) => {

    setCart(previousCart =>
        previousCart.filter(item => item.id !== id)
    );

};

    return (

        <>

            <Navbar
    setPage={setPage}
    cartCount={cart.reduce(
        (total, item) => total + item.quantity,
        0
    )}
/>


            {page === "home" && (
                <Home setPage={setPage} />
            )}


            {page === "menu" && (

                <Menu
                    foods={foods}
                    loading={loading}
                    error={error}
                    addToCart={addToCart}
                />

            )}
            
            {page === "cart" && (

    <Cart
        cart={cart}
        increaseQuantity={increaseQuantity}
        decreaseQuantity={decreaseQuantity}
        removeFromCart={removeFromCart}
    />

)}

        </>

    );

}


/* =========================
   Render App
========================= */

const root = ReactDOM.createRoot(
    document.getElementById("root")
);

root.render(<App />);
