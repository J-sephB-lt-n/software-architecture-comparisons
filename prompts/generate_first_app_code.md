I am writing a simple e-commerce shopping cart/order system in python.
The point of this app is that I am going to refactor it multiple times in order to show how it will look under these different architectures:

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

My first step is to implement this application in a single script with no particular architecture.

Here are my requirements:

- application written in python 3.13
- sqlite for data persistence

The application is accessed using a subcommand-style CLI like git.
Here are the required commands:

```bash
shop auth login --username joe --password admin1234
shop auth logout --username joe
shop products list
shop products view --product_id 69
shop cart add --product_id 69 --quantity 1
shop cart remove --product_id 69
shop cart update --product_id 69 --quantity 3
shop cart view
shop cart discount list   # list available discount vouchers
shop cart discount apply --voucher-id 12
shop cart total
shop order checkout --payment-method visa
shop order cancel --order_id 420
shop order status --order_id 420
shop order history
```
