fn main() {
    println!("rust online");
    loop {
        println!("alive");
        std::thread::sleep(std::time::Duration::from_secs(30));
    }
}
