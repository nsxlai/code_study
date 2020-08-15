"""
source: https://medium.com/@severinperez/effective-program-structuring-with-the-dependency-inversion-principle-2d5adf11f863

Put concisely, the DIP says that high- and low-level modules should depend on mutual abstractions, and furthermore,
that details should depend on abstractions rather than vice versa.

The original code was written in C#
"""
class Restaurant:
        {
            public string Name { get; set; }

    public ICooker Cooker { get; set; }

    public Restaurant(string name, ICooker cooker)
    {
        this.Name = name;
    this.Cooker = cooker;
    }

    public void Cook(string item)
    {
        this.Cooker.TurnOn();
    this.Cooker.Cook(item);
    this.Cooker.TurnOff();
    }
    }

    interface ICooker
    {
        bool On { get; set; }

    void TurnOn();

    void TurnOff();

    void Cook(string item);
    }

    class Oven : ICooker
    {
        public bool On { get; set; }

    public void TurnOn()
    {
        Console.WriteLine("Turning on the oven!");
    this.On = true;
    }

    public void TurnOff()
    {
        Console.WriteLine("Turning off the oven!");
    this.On = false;
    }

    public void Cook(string item)
    {
    if (!this.On)
    {
        Console.WriteLine("Oven not turned on.");
    }
    else
    {
        Console.WriteLine("Now baking " + item + "!");
    }
    }
    }

    class Stove : ICooker
    {
        public bool On { get; set; }

    public void TurnOn()
    {
        Console.WriteLine("Turning on the stove!");
    this.On = true;
    }

    public void TurnOff()
    {
        Console.WriteLine("Turning off the stove!");
    this.On = false;
    }

    public void Cook(string item)
    {
    if (!this.On)
    {
        Console.WriteLine("Stove not turned on.");
    }
    else
    {
        Console.WriteLine("Now frying " + item + "!");
    }
    }
    }
    }

if __name__ == '__main__':
    class Program
    {
        static void Main(string[] args)
{
    var bakery = new Restaurant("Bakery", new Oven());
bakery.Cook("cookies");

var crepery = new Restaurant("Crepery", new Stove());
crepery.Cook("crepes");
}
}