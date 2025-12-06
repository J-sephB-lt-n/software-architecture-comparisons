I am writing a simple e-commerce shopping cart/order system in python.
The point of this app is that I am going to refactor it multiple times in order to show how it looks under these different architectures:

- Clean
- Command Query Responsibility Segregation (CQRS)
- Event-driven
- Service-Oriented
- Modular monolith
- Ports and adapters (hexagonal)
- n-tier
- layered
- MVC
- vertical slice
- domain-driven design
- onion
- microservices

I have chosen to implement the following functionality in the app:

- User auth (to show cross-cutting concerns)
- List products
- View product details
- Product search
- Add item to cart
- Remove item from cart
- Update item quantity in cart
- View cart
- Calculate cart total (with and without shipping and tax)
- Apply discount code
- Place order (checkout)
- Cancel order
- Check/Reserve/Free inventory
- Call payment gateway
- Order lifecycle (order status)
- View order history

The application is accessed using a subcommand-style CLI like git.
Here are the required commands:

```bash
shop auth login --username admin --password password
shop auth logout
shop products list
shop products view --product_id 69
shop cart add --product_id 69 --quantity 1
shop cart remove --product_id 69
shop cart update --product_id 69 --quantity 3
shop cart view
shop cart apply-discount --discount_code SUMMER26
shop cart total
shop order checkout --payment-method visa
shop order cancel --order_id 420
shop order status --order_id 420
shop order history
```

I am storing all of the app data in a SQL database. Will the choice of architecture affect the schemas in this SQL database?
